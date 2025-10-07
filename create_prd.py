import os
import glob

def extract_user_story_info(file_path):
    """Extract relevant information from a user story file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the user story ID and title
    lines = content.split('\n')
    title = ""
    user_story = ""
    criteria = []
    details = []
    
    # Find the title (could be in different formats)
    for line in lines:
        if line.startswith('# ') and 'HU' in line:
            title = line.replace('# ', '')
            break
        elif line.startswith('## ') and 'HU' in line:
            title = line.replace('## ', '')
            break
    
    # Extract the user story (as a user I want to...)
    in_story = False
    for i, line in enumerate(lines):
        if 'Como ' in line and ('Quiero' in lines[i+1] or 'quiero' in lines[i+1]):
            in_story = True
            user_story = line + '\n'
            continue
        if in_story and ('Para' in line or 'para' in line):
            user_story += lines[i-1] + '\n' + line
            in_story = False
            continue
        if in_story:
            user_story += line + '\n'
    
    # Extract acceptance criteria
    in_criteria = False
    for line in lines:
        if '### Criterios de Aceptación' in line or '## Criterios de Aceptación' in line:
            in_criteria = True
            continue
        elif in_criteria and line.startswith('###') or line.startswith('##'):
            in_criteria = False
            continue
        elif in_criteria and line.strip() and not line.startswith('#'):
            criteria.append(line)
    
    # Extract technical details if available
    in_details = False
    for line in lines:
        if '### Detalles Técnicos' in line or '## Detalles Técnicos' in line:
            in_details = True
            continue
        elif in_details and line.startswith('###') or line.startswith('##'):
            in_details = False
            continue
        elif in_details and line.strip() and not line.startswith('#'):
            details.append(line)
    
    return {
        'title': title,
        'user_story': user_story,
        'criteria': criteria,
        'details': details,
        'file_path': file_path
    }

def create_prd():
    """Create a PRD file from all user stories."""
    # Get all user story files
    user_stories_dir = 'docs/user_stories'
    md_files = []
    
    # Recursively find all .md files except README.md and slices.md
    for root, _, files in os.walk(user_stories_dir):
        for file in files:
            if file.endswith('.md') and file not in ['README.md', 'slices.md']:
                md_files.append(os.path.join(root, file))
    
    # Sort files by their names to maintain order
    md_files.sort()
    
    # Extract information from each file
    stories = []
    for file_path in md_files:
        story_info = extract_user_story_info(file_path)
        stories.append(story_info)
    
    # Create the PRD content
    prd_content = "# Documento de Requisitos del Producto (PRD) - HCDSys\n\n"
    prd_content += "## Resumen del Proyecto\n\n"
    prd_content += "HCDSys es un sistema de gestión documental para el Honorable Concejo Deliberante que permite la búsqueda, "
    prd_content += "gestión y acceso controlado a documentos digitales.\n\n"
    
    prd_content += "## Objetivos del Proyecto\n\n"
    prd_content += "- Facilitar la búsqueda rápida de documentos\n"
    prd_content += "- Permitir la gestión organizada de documentos\n"
    prd_content += "- Proporcionar acceso controlado según roles de usuario\n"
    prd_content += "- Mantener un registro histórico de documentos\n\n"
    
    prd_content += "## Historias de Usuario\n\n"
    
    # Group stories by slice
    slices = {}
    for story in stories:
        slice_name = os.path.basename(os.path.dirname(story['file_path']))
        if slice_name not in slices:
            slices[slice_name] = []
        slices[slice_name].append(story)
    
    # Add stories to PRD by slice
    for slice_name, slice_stories in sorted(slices.items()):
        prd_content += f"### {slice_name.replace('_', ' ').title()}\n\n"
        
        for story in slice_stories:
            prd_content += f"#### {story['title']}\n\n"
            prd_content += f"{story['user_story']}\n"
            
            if story['criteria']:
                prd_content += "**Criterios de Aceptación:**\n\n"
                for criterion in story['criteria']:
                    prd_content += f"- {criterion.strip()}\n"
                prd_content += "\n"
            
            if story['details']:
                prd_content += "**Detalles Técnicos:**\n\n"
                for detail in story['details']:
                    prd_content += f"- {detail.strip()}\n"
                prd_content += "\n"
    
    # Write the PRD to a file
    output_path = '.taskmaster/docs/prd.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prd_content)
    
    print(f"PRD generado exitosamente en: {output_path}")

if __name__ == "__main__":
    create_prd()
