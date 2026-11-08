# 多语言生成

以 en/ 下的英文页面为模板，按 *.json 里的翻译生成其他 8 种语言，并给所有页面加语言菜单。

改了英文页面后：

    python3 i18n/extract.py .   # 重新提取英文文字到 i18n/en.json（编号可能变化，需核对翻译）
    python3 i18n/build.py .     # 生成 es/ pt/ fr/ de/ ja/ ko/ ar/ id/

（extract.py 会把 en.json 写到当前目录，请在 i18n/ 目录里运行：cd i18n && python3 extract.py .. && python3 build.py ..）
