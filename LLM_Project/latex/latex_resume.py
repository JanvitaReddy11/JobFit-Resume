def latex_resume(candidate_data, output_filename='resume.tex'):
    """
    Generates a LaTeX resume file based on candidate data.

    :param candidate_data: Dictionary containing candidate information.
    :param output_filename: Name of the output LaTeX file.
    """
    latex_content = r"""
    \documentclass{resume}

    \begin{document}
    """

    # Add Name and Address
    latex_content += f"\\name{{{candidate_data['name']}}}\n"
    list_d = [candidate_data['contact'][key] for key in candidate_data['contact']]
    latex_content += f"\\details{{{list_d[0]}}} {{{list_d[1]}}} {{{list_d[2]}}}{{{list_d[3]}}}\n"

    # Education Section
    latex_content += r"\begin{rSection}{Education}" + "\n"
    for edu in candidate_data['education']:
        latex_content += f"""
\\begin{{rSubsectionedu}}{{{edu['institution']}}}{{{edu['location']}}}{{{edu['duration']}}}{{{edu['degree']}}}{{{edu['major']}}}{{{edu['cgpa']}}}\n
"""
        latex_content += r"\end{rSubsectionedu}" + "\n"
        latex_content += r"\vspace{-15pt}" + "\n"
    latex_content += r"\end{rSection}" + "\n"

    # Skills Section
    latex_content += r"\begin{rSection}{Skills}" + "\n"
    latex_content += r"\begin{itemize}[left=0pt, label={}, align=parleft]" + "\n"
    for skill_name, skill_list in candidate_data['skills'].items():
        latex_content += r"\vspace{-5pt}" + "\n"
        latex_content += f"\\item [] \\textbf{{{skill_name.capitalize()}}}: "
        latex_content += ", ".join([f"{{{skill}}}" for skill in skill_list])
        latex_content += "\n"
    latex_content += r"\end{itemize}" + "\n"
    latex_content += r"\end{rSection}" + "\n"

    # Work Experience Section
    latex_content += r"\begin{rSection}{Work Experience}" + "\n"
    for work in candidate_data['work experience']:
        latex_content += r"\vspace{-3pt}" + "\n"
        latex_content += f"""
\\begin{{rSubsectionWork}}{{{work['title']}}}{{{work['company']}}}{{{work['location']}}}{{{work['duration']}}}\n
"""
        for detail in work['responsibilities']:
            latex_content += r"\vspace{-3pt}" + "\n"
            latex_content += f"\\item {detail}\n"
        latex_content += r"\end{rSubsectionWork}" + "\n"
    latex_content += r"\end{rSection}" + "\n"

    # Projects Section
    latex_content += r"\begin{rSection}{Projects}" + "\n"
    proj = candidate_data.get('projects', [])


    if isinstance(proj, dict) and 'projects' in proj:
        proj = proj['projects']

    for project in proj:
        latex_content += r"\vspace{-3pt}" + "\n"
        latex_content += f"""
    \\begin{{rSubsectionProj}}{{{project['title']}}}\n
    """
        for detail in project['description']:
            latex_content += r"\vspace{-3pt}" + "\n"
            latex_content += f"\\item {detail}\n"
        latex_content += r"\end{rSubsectionProj}" + "\n"
    latex_content += r"\end{rSection}" + "\n"

    latex_content += r"\end{document}"

    with open(output_filename, 'w') as file:
        file.write(latex_content)

    print(f"LaTeX file created: {output_filename}")
