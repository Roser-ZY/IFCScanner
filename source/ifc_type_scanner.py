import os
import re
import json
from pyecharts.options import LabelOpts, InitOpts, TreeItem
from pyecharts.charts import Tree

class IfcTypeScanner:
    report_root = "ROOT"
    report_careful_nodes = [
        
    ]
    report_filepath = ""
    class_dict = {}
    ifc_tree = {}
    
    def __init__(self, report_filepath):
        self.report_filepath = report_filepath
    
    def find(self, directory, target_class, chunk_size=8*1024*1024):
        print("Find " + target_class + " from " + directory + ".")
        # WARNING: Read by chunks may miss some type.
        filenames = os.listdir(directory)
        target_class_upper = target_class.upper()
        if len(filenames) == 0:
            print("There are no IFC files to scan.")
        for filename in filenames:
            with open(directory + '\\' + filename, "r") as ifc_file:
                while True:
                    chunk_data = ifc_file.read(chunk_size)
                    if not chunk_data:
                        break
                    end = chunk_data.rfind('\n')
                    if end == -1:
                        end = len(chunk_data)
                    for name in re.findall("= IFC[A-Z0-9]*", chunk_data[0:end]):
                        if name[2:] == target_class_upper:
                            return filename
    
    def scan(self, inheritance_filepath, directory, chunk_size=8*1024*1024):
        with open(inheritance_filepath, "r") as file:
            self.class_dict = json.load(file)
        
        for k in self.class_dict.keys():
            self.class_dict[k]["Count"] = 0
        for chunk_data in self.__read_chunks(directory, chunk_size):
            self.__record_types(chunk_data)
        
        with open(self.report_filepath, "w") as report_file:
            json.dump(self.class_dict, report_file)
        
    def present(self, title="Presentation"):
        with open(self.report_filepath, "r") as report_file:
            self.class_dict = json.load(report_file)
        root_node = self.__generate_report_tree(self.class_dict[self.report_root])
        root_item = self.__transform_dict_to_tree_item(root_node)
        
        Tree(
            init_opts=InitOpts(
                width="4800px",
                height="2560px",
                page_title=title
            )
        ).add(
            series_name=title,
            data=[root_item],
            pos_top="30",
            pos_bottom="30",
            pos_left="50",
            pos_right="50",
            collapse_interval=200,
            initial_tree_depth=20,
            is_roam=True,
            label_opts=LabelOpts(
                position="top"
            ),
            leaves_label_opts=LabelOpts(
                color="#009688"
            )
        ).render(path=title + ".html")
        
    def __read_chunks(self, directory, chunk_size):
        # WARNING: Read by chunks may miss some type.
        filenames = os.listdir(directory)
        if len(filenames) == 0:
            print("There are no IFC files to scan.")
        for filename in filenames:
            print("Scanning " + filename + ".")
            with open(directory + '\\' + filename, "r") as ifc_file:
                while True:
                    chunk_data = ifc_file.read(chunk_size)
                    if not chunk_data:
                        break
                    yield chunk_data

    def __record_types(self, chunk_data:str):
        end = chunk_data.rfind('\n')
        if end == -1:
            end = len(chunk_data)
        for name in re.findall("= IFC[A-Z0-9]*", chunk_data[0:end]):
            self.class_dict[name[2:]]["Count"] += 1
    
    def __generate_report_tree(self, curr_node):
        report_node = {
            "name": curr_node["ClassName"],
            "value":0,
            "children": []
        }
        
        for child_name in curr_node["Children"]:
            child_report_node = self.__generate_report_tree(self.class_dict[child_name])
            
            if child_report_node["value"] > 0:
                report_node["value"] += child_report_node["value"]
                report_node["children"].append(child_report_node)
        
        report_node["value"] += curr_node["Count"]
            
        return report_node
    
    def __transform_dict_to_tree_item(self, curr_report_node):
        child_item_list = []
        for child_node in curr_report_node["children"]:
            child_item_list.append(self.__transform_dict_to_tree_item(child_node))
            
        report_tree_item = None
        if curr_report_node["name"] in self.report_careful_nodes:
            return TreeItem(
                name=curr_report_node["name"],
                value=curr_report_node["value"],
                children=child_item_list,
                label_opts=LabelOpts(color="#FF5252")
            )
        else:
            return TreeItem(
                name=curr_report_node["name"],
                value=curr_report_node["value"],
                children=child_item_list
            )
    
    