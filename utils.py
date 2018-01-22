def randomword(length):
    import random, string
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def doc_get_page_num(file_name, file_ext):
    if file_ext == '.pdf':
        from PyPDF2 import PdfFileReader
        pdf = PdfFileReader(open(file_name,'rb'))
        return (pdf.getNumPages(), file_name)
    elif file_ext in ['.doc', '.docx']:
        import subprocess
        file_prefix = file_name[:-len(file_ext)]
        pdf_filename = file_prefix + '.pdf'
        # try:
        #     subprocess.check_call(['unoconv', '-f', 'pdf', '-o', pdf_filename, '-d', 'document', file_name])
        # except subprocess.CalledProcessError as e:
        #     print('CalledProcessError', e)

        import cloudconvert
        import buu_config

        config = buu_config.config()

        api = cloudconvert.Api(config.convert_api)

        process = api.convert({
            'inputformat': file_ext[1:],
            'outputformat': 'pdf',
            'input': 'upload',
            'file': open(file_name, 'rb')
        })
        process.wait() # wait until conversion finished
        process.download(pdf_filename) # download output file

        from PyPDF2 import PdfFileReader
        pdf = PdfFileReader(open(pdf_filename,'rb'))
        return (pdf.getNumPages(), pdf_filename)
