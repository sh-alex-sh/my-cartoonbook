import sys
sys.path.insert(0, '.')
from services.pdf_parser import DocumentParser
p = DocumentParser()
try:
    c = p.extract_text(r'D:\ai-project\my-test\uploads\1de9e25b-0f6d-494f-a612-a9a329e11eb8_01.pdf')
    print('SUCCESS:', len(c), 'chars')
except Exception as e:
    print('ERROR:', e)
    import traceback
    traceback.print_exc()