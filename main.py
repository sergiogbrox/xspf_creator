import os
import sys
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom

def get_ffprobe_path():
    if hasattr(sys, '_MEIPASS'):
        # Se estiver rodando como executável gerado pelo PyInstaller,
        # os dados extras estarão dentro de sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # Caso contrário, use o diretório "bin" dentro do projeto
        base_path = os.path.abspath("bin")
    return os.path.join(base_path, "ffprobe.exe")

def get_video_duration(file_path):
    ffprobe_path = get_ffprobe_path()
    try:
        result = subprocess.run(
            [
                ffprobe_path, '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # <-- Desvia stderr para /dev/null (não imprime erro)
            text=True
        )
        duration_sec = float(result.stdout.strip())
        return int(duration_sec * 1000)
    except:
        # Não imprime nada, apenas retorna -1
        return -1

def is_video_file(filename):
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.mpeg', '.mpg']
    ext = os.path.splitext(filename)[1].lower()
    return ext in video_extensions

class FolderNode:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.subfolders = []
        self.files = []

def build_tree(root_path, include_root_node=True):
    root_path = os.path.abspath(root_path)

    def _build(current_path):
        folder_name = os.path.basename(current_path)
        node = FolderNode(folder_name, current_path)
        try:
            items = sorted(os.listdir(current_path))
        except PermissionError:
            return node
        for item in items:
            full_item_path = os.path.join(current_path, item)
            if os.path.isdir(full_item_path):
                node.subfolders.append(_build(full_item_path))
            else:
                if is_video_file(item):
                    node.files.append(full_item_path)
        return node

    root_node = _build(root_path)
    if not include_root_node:
        return root_node.subfolders
    else:
        return [root_node]

def assign_track_ids(folder_nodes, all_tracks):
    def _assign(node):
        for f in node.files:
            track_id = len(all_tracks)
            all_tracks.append({'path': f, 'track_id': track_id})
        for sub in node.subfolders:
            _assign(sub)
    for fn in folder_nodes:
        _assign(fn)

def create_tracklist(parent, all_tracks):
    trackList_elem = ET.SubElement(parent, 'trackList')
    for track_info in all_tracks:
        path = track_info['path']
        track_id = track_info['track_id']

        track_elem = ET.SubElement(trackList_elem, 'track')
        loc_elem = ET.SubElement(track_elem, 'location')
        file_url = Path(path).resolve().as_uri()
        loc_elem.text = file_url

        duration_elem = ET.SubElement(track_elem, 'duration')
        duration_val = get_video_duration(path)
        duration_elem.text = str(duration_val)

        ext_elem = ET.SubElement(track_elem, 'extension', application="http://www.videolan.org/vlc/playlist/0")
        vlc_id_elem = ET.SubElement(ext_elem, '{http://www.videolan.org/vlc/playlist/ns/0/}id')
        vlc_id_elem.text = str(track_id)

def build_vlc_nodes(parent, folder_nodes, all_tracks):
    path_to_id = {t['path']: t['track_id'] for t in all_tracks}

    def _create_node(folder_node, parent_node):
        node_elem = ET.SubElement(parent_node, '{http://www.videolan.org/vlc/playlist/ns/0/}node')
        node_elem.set('title', folder_node.name)

        for f in folder_node.files:
            track_id = path_to_id.get(f)
            if track_id is not None:
                item_elem = ET.SubElement(node_elem, '{http://www.videolan.org/vlc/playlist/ns/0/}item')
                item_elem.set('tid', str(track_id))

        for sub in folder_node.subfolders:
            _create_node(sub, node_elem)

    for fn in folder_nodes:
        _create_node(fn, parent)

def create_xspf_playlist(root_directory, output_file):
    if not output_file.lower().endswith('.xspf'):
        output_file += '.xspf'

    ET.register_namespace('', "http://xspf.org/ns/0/")
    ET.register_namespace('vlc', "http://www.videolan.org/vlc/playlist/ns/0/")

    folder_nodes = build_tree(root_directory, include_root_node=False)
    all_tracks = []
    assign_track_ids(folder_nodes, all_tracks)

    playlist_elem = ET.Element('playlist', version="1")
    title_elem = ET.SubElement(playlist_elem, 'title')
    title_elem.text = "Lista de reprodução"

    create_tracklist(playlist_elem, all_tracks)

    extension_elem = ET.SubElement(playlist_elem, 'extension', application="http://www.videolan.org/vlc/playlist/0")
    build_vlc_nodes(extension_elem, folder_nodes, all_tracks)

    xml_str = ET.tostring(playlist_elem, encoding='utf-8')
    parsed = xml.dom.minidom.parseString(xml_str)
    pretty_xml = parsed.toprettyxml(indent="    ")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    print(f"Playlist criada com sucesso: {output_file}")

if __name__ == '__main__':
    try:
        print("Bem-vindo ao criador de playlist XSPF!\n")
        print("Digite o caminho da pasta desejada ou pressione Enter em branco para usar a pasta atual.\n")

        folder_input = input("Caminho da pasta: ").strip()

        if folder_input == "":
            # Usar a pasta atual
            root_dir = os.getcwd()
            print(f"\nNenhum caminho informado. Usando a pasta atual:\n{root_dir}\n")
        else:
            root_dir = folder_input
            print(f"\nVocê digitou o caminho:\n{root_dir}\n")

        output_playlist = "Playlist.xspf"
        create_xspf_playlist(root_dir, output_playlist)

    except Exception as e:
        print("Ocorreu um erro inesperado:", e)

    finally:
        input("Pressione qualquer tecla para sair...")
