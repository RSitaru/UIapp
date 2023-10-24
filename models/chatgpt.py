import os
import tempfile
from docx import Document
import openai
import concurrent.futures

# OpenAI configuration
openai.organization = "org-2RniczpRsyTC1u0YUI5ebhAa"
openai.api_key = "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"

ALLOWED_EXTENSIONS_DOCX = {'docx'}

def allowed_file(filename, allowed_extensions=ALLOWED_EXTENSIONS_DOCX):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def process_docx(file_path, prompt):
    # Check if it's a valid file type
    if not allowed_file(file_path):
        raise ValueError('Invalid file type')

    try:
        return create_modified_docx(file_path, prompt)
    except Exception as e:
        raise ValueError(f"Error processing the DOCX file: {str(e)}")

def create_modified_docx(file_path, prompt):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
        doc = Document(file_path)
        full_text = '\n'.join([para.text for para in doc.paragraphs])
        CHUNK_SIZE = 4000
        text_chunks = [full_text[i:i + CHUNK_SIZE] for i in range(0, len(full_text), CHUNK_SIZE)]
        
        # Concurrently processing the text chunks
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_chunk, text_chunks, [prompt] * len(text_chunks)))

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        safe_filename = ''.join([c if c.isalnum() else '_' for c in base_name])
        output_filename = f"{safe_filename}_processed.docx"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)

        output_doc = Document()
        for result in results:
            output_doc.add_paragraph(result)

        output_doc.save(output_path)

        return output_path

def process_chunk(chunk, prompt):
    messages = [{
        "role": "user",
        "content": f"{prompt} {chunk}"
    }]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message['content'].strip()

