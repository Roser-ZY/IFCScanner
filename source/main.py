from ifc_type_scanner import IfcTypeScanner

if __name__ == '__main__':
    scanner = IfcTypeScanner("烽燧IFC类型汇总.json")
    # scanner.scan("./ifc_spider/ifc_inheritance.json", "D:\Work\Develop\BC\IFC 导入\model\烽燧IFC文件")
    scanner.present("烽燧IFC类型汇总")