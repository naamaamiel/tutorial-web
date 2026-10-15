import os
import pathlib
import shutil

#
# A painfully human-written helper script to turn add workspace folder files to the site
#

# Helper: workspace file/dir name to website file/dir name
def work_name_to_web_name(work_name, unit):
  first_hyphen = work_name.find('-')

  if first_hyphen != 2:
    # completed folder -> completed folder
    if work_name == "completed":
      return "completed"
    # code file -> code file OR m5out dir -> m5out dir OR intermediate dir -> intermediate dir
    else:
      no_under = work_name.replace("_", "-")
      return f"{(no_under.replace('.', '-'))}.md"
  else:
    front_num = work_name[0:first_hyphen]
    # specific edge case of some other file/dir with two characters before first hyphen
    if (not front_num.isdigit()):
      no_under = work_name.replace("_", "-")
      return f"{(no_under.replace('.', '-'))}.md"
    
    # unit folder -> unit folder
    if (unit == ""):
      return front_num + '-unit-' + convert_to_roman(int(front_num))
    else:
      # section folder -> section folder
      return unit + '-' + front_num

# Helper: convert to roman numeral
# being lazy for now with a map; I *doubt* we'll have more than 10 units
def convert_to_roman(num):
  map = {1 : "i",
         2 : 'ii',
         3 : "iii",
         4 : "iv",
         5 : "v",
         6 : "vi",
         7 : "vii",
         8 : "viii",
         9 : "ix",
         10 : "x"}
  return map[num]

# Helper: grab the unit number (or whatever is before the first hyphen) from a name
def unit_num(name):
   return name[0:name.find('-')]

# Helper: convert a workspace directory path to its corresponding web directory path
def work_path_to_web_path(work_path):
  web_path = ""
  count = 0
  unit = ""
  for step in work_path.split('/'):
    match count:
      case 0:
        pass
      case 1:
        web_path = web_path + f"{step}_pages"
      case 2:
        web_path =  web_path + "/" + work_name_to_web_name(step, "")
        unit = unit_num(step)
      case 3:
        if unit != "04":
          web_path = web_path + "/" + unit + "-" + unit_num(step)
        else:
          web_path =  web_path + "/" + unit_num(step) + "/" + unit_num(step) + "-"
          count = -2 # Weird hack for Unit IV (sigh)
      case -1: # Weird hack, continued
        web_path = web_path + unit_num(step)
        count = 4
      case _:
        web_path = web_path + "/" + step
    count += 1
  return web_path

# Titles for webpages (otherwise cannot be determined by file name)
unit_titles = ["Unit I: Introduction", "Unit II: Beginning Simulation", "Unit III: Intermediate Features", "Unit IV: Developing gem5 Models", "Unit V: Advanced Topics"]
track_titles = {"04a": "Unit IV: Processors Track", 
                "04b": "Unit IV: Caches Track", 
                "04c": "Unit IV: Memory Track"}
sections = {"01-01" : "Section 1: Why simulation?",
            "01-02" : "Section 2: Enter gem5",
            "01-03" : "Section 3: Installing gem5",
            "01-04" : "Section 4: Your first configuration script",
            "02-01" : "Section 1: The gem5 standard library and resources",
            "02-02" : "Section 2: Processors",
            "02-03" : "Section 3: Caches",
            "02-04" : "Section 4: Memory",
            "03-01" : "Section 1: Simulation modes",
            "03-02" : "Section 2: gem5 resources",
            "03-03" : "Section 3: Traffic generators",
            "03-04" : "Section 4: Communication from simulation to simulator",
            "04a-01" : "Section 1: SimObjects",
            "04a-02" : "Section 2: Event-driven simulation",
            "04a-03" : "Section 3: Ports",
            "04a-04" : "Section 4: Debugging",
            "04a-05" : "Section 5: Branch predictors",
            "04a-06" : "Section 6: ISAs",
            "05-01" : "Section 1: KVM fast-forwarding",
            "05-02" : "Section 2: Checkpointing",
            "05-03" : "Section 3: Sampled simulation",
            "05-04" : "Section 4: MultiSim",
            "05-05" : "Section 5: Disk images",
            "05-06" : "Section 6: Power modeling",
}

# Convert file extension to corresponding markdown syntax highlight keyword
syntax_highlights = {".py" : "python",
                     ".cc" : "cpp",
                     ".c" : "c",
                     ".txt" : "txt",
                     ".json" : "json",
                     ".hh" : "cpp",
                     ".h" : "c",
                     ".bib" : "bibtex"
                    }

# Crawl workspace files and make missing website files along the way
curr_unit_dir = ""
curr_section_dir = ""
curr_web_root = "workspace_pages"
parent_web_names = {}
for root, dirs, files in os.walk("_includes/workspace"):
  path = pathlib.Path(root)
  path_name = path.name
  parent = path.parent
  parent_name = path.parent.name
  #
  # DIRECTORY HANDLING
  #
  # Figure out where we are by the root
  if (root == "_includes/workspace"):
    # Ok, we're looking at our units here
    # Make unit folders if necessary
    for unit_dir in dirs:
      unit_dir_name = work_name_to_web_name(pathlib.Path(unit_dir).name, curr_unit_dir)
      filepath = f"{curr_web_root}/{unit_dir_name}"
      if not os.path.exists(filepath):
        os.mkdir(filepath)
        print(f"Made unit directory: {filepath}")
  else:
    path_length = root.count('/')
    # Ok, we have our unit directories all done
    # If we're looking into a unit directory, set the unit number accordingly
    if path_length == 2:
      curr_unit_dir = path_name
      curr_web_root = f"workspace_pages/{work_name_to_web_name(curr_unit_dir, '')}"
      parent_web_names[path] = unit_titles[int(unit_num(curr_unit_dir)) - 1]
    # If we're looking into a section directory, make a corresponding one in web if necessary
    # Make an exception for unit 4, with has tracks (ugh)
    elif path_length == 3 or (path_length == 4 and unit_num(curr_unit_dir) == "04"):
      section_dir_name = work_name_to_web_name(path_name, unit_num(curr_unit_dir))
      curr_section_dir = section_dir_name
      # Annoying unit 4 exception
      if path_length == 4:
        unit_4_exception = f"{parent_name[0:parent_name.find('-')]}"
        section_dir_name = f"{unit_4_exception}-{unit_num(path_name)}"
        curr_section_dir = f"{unit_4_exception}/{section_dir_name}"
      else:
        unit_4_exception = ""
        if (unit_num(curr_unit_dir) == "04"): 
          section_dir_name = unit_num(section_dir_name) # I hate unit 4
          curr_section_dir = section_dir_name
          parent_web_names[path] = track_titles[section_dir_name]

      filepath = f"{curr_web_root}/{curr_section_dir}"
      workspace_title = f"{section_dir_name} Workspace"
      parent_web_names[path] = workspace_title
      # Make the directory
      if not os.path.exists(filepath):
        os.mkdir(filepath)
        print(f"Made section directory: {filepath}")

      if not (path_length == 3 and unit_num(curr_unit_dir) == "04"):
        # Make the table-of-contents "workspace" page
        toc_path = f"{filepath}/00-workspace.md"
        if not os.path.exists(toc_path):
          # Make front matter
          front_matter = ("---\n"
                          f"title: \"{workspace_title}\"\n"
                          f"parent: \"{sections[section_dir_name]}\"\n"
                          f"layout: default\n"
                          f"nav_order: 1\n"
                          "---\n"
                          ""
          )
          # Make and write to the file
          with open(toc_path, 'w', encoding="utf-8") as toc_file:
            toc_file.write(front_matter)
          print(f"Made workspace table-of-contents file for {toc_path}")
    else:
      # The wild west of subdirectories!

      # Make the directory
      filepath = f"{curr_web_root}/{curr_section_dir}"
      work_path = root
      depth = filepath.count('/') + 2 # get rid of _includes/workspace
      while depth > 0:
        work_path = work_path[work_path.find('/')+1:]
        depth -= 1

      full_dir_path = f"{filepath}/{work_path}"

      if not os.path.exists(full_dir_path):
        os.mkdir(full_dir_path)
        print(f"Made subdirectory: {full_dir_path}")

      # Make the table of contents
      # One special case: are we looking right at the "completed" directory?
      # If so, it has a different parent in the front matter and needs to be handled separately
      file_name = work_name_to_web_name(path_name, unit_num(curr_unit_dir))
      if (file_name == "completed"):
        file_title = f"{curr_section_dir[curr_section_dir.find('/') + 1 :]} Completed Files"
        parent_web_names[path] = file_title
        # Create front matter
        front_matter = ("---\n"
                f"title: \"{file_title}\"\n"
                f"parent: \"{sections[filepath[filepath.rfind('/') + 1:]]}\"\n"
                f"ancestor: \"{sections[curr_section_dir[curr_section_dir.find('/') + 1 :]]}\"\n"
                f"layout: default\n"
                f"nav_order: 2\n"
                "---\n"
                ""
        )
        file_path = f"{full_dir_path}/00-completed.md"
        if not os.path.exists(file_path):
          # Make and write to the file
          with open(file_path, 'w', encoding="utf-8") as comp_file:
            comp_file.write(front_matter)
          print(f"Made completed table-of-contents file for {filepath}/{path_name}")
      # Just normal subdirectory things
      else:
        parent_web_names[path] = path_name
        # Create front matter
        grandparent = parent.parent.name
        ancestor = sections[curr_section_dir[curr_section_dir.find('/') + 1 :]]
        if grandparent not in full_dir_path:
          grandparent = ancestor
        if grandparent == "completed":
          grandparent = f"{curr_section_dir[curr_section_dir.find('/') + 1 :]} Completed Files"
        elif "completed" in full_dir_path:
          ancestor = f"{curr_section_dir[curr_section_dir.find('/') + 1 :]} Completed Files"
        front_matter = ("---\n"
                f"title: \"{path_name}\"\n"
                f"parent: \"{parent_web_names[parent]}\"\n"
                f"grand_parent: \"{grandparent}\"\n"
                f"ancestor: \"{ancestor}\"\n"
                f"layout: default\n"
                f"nav_order: 2\n"
                "---\n"
                ""
        )
        file_path = f"{full_dir_path}/{file_name}"
        if not os.path.exists(file_path):
          # Make and write to the file
          with open(file_path, 'w', encoding="utf-8") as sub_file:
            sub_file.write(front_matter)
          print(f"Made table-of-contents file for {filepath}/{path_name}")

  #
  # FILE HANDLING
  #
  # Get the full web path
  full_dir_path = work_path_to_web_path(root)

  count = 0
  for file in files:

    # Prepare to make the front matter

    # Determine the correct parent
    filename = work_name_to_web_name(file, unit_num(curr_unit_dir))
    if parent_web_names.__contains__(path):
      parent_web_name = parent_web_names[path]
    else:
      parent_web_name = parent_name

    # Determine the correct grandparent
    # Also determine great-grandparent to put in "ancestor" field
    web_path = pathlib.Path(full_dir_path)

    grandparent_work_dir = web_path.parent
    grandparent_name = grandparent_work_dir.name
    grandparent = grandparent_name

    great_work_dir = grandparent_work_dir.parent
    ancestor_name = great_work_dir.name
    ancestor = ancestor_name

    if grandparent_name in sections:                      # files one level down from the "workspace" directory
       if web_path.name == "completed":                           # If completed, these are "shallow" and don't have the workspace as parent
         grandparent = sections[grandparent_name]
         ancestor = ancestor = unit_titles[int(unit_num(curr_unit_dir)) - 1]
       else:
        grandparent = f"{grandparent_name} Workspace"           # grandparent is just the workspace page
        ancestor = sections[grandparent_name]                   # great-grandparent is then just the section page
    elif grandparent_name == "completed":                 # files under the "completed" directory
      grandparent = f"{ancestor_name} Completed Files"         # grandparent is just the completed files page
      ancestor = sections[ancestor_name]                       # great-grandparent is then just the section page
    elif grandparent_name == work_name_to_web_name(curr_unit_dir, ""):  # shallow files with a unit as parent
      grandparent = sections[web_path.name]                     # grandparent is the section page
      ancestor = unit_titles[int(unit_num(curr_unit_dir)) - 1]  # ancestor is the unit page
    elif grandparent_name == "04a" or grandparent_name == "04b" or grandparent_name == "04c":  # unit 4 exception strikes again
      grandparent = sections[web_path.name]                     # grandparent is the section page
      ancestor = track_titles[grandparent_name]                 # ancestor is the track page
    else:
      # leave the grandparent alone; it's some subdirectory
      # check if the ancestor is also some subdirectory or it it's the completed or workspace files
      if ancestor_name in sections:
        ancestor = f"{ancestor_name} Workspace"
      elif ancestor_name == "completed":
        ancestor = f"{great_work_dir.parent.name} Completed Files"
      # ancestor page can't be anything else--all files are under either the workspace or the completed directory eventually
    
    # Build the front matter
    front_matter = ("---\n"
                    f"title: \"{file}\"\n"
                    f"parent: \"{parent_web_name}\"\n"
                    f"grand_parent: \"{grandparent}\"\n"
                    f"ancestor: \"{ancestor}\"\n"
                    f"layout: default\n"
                    f"nav_order: {count}\n"
                    "---\n"
                    ""
    )

    # Build the contents
    contents = ""
    # Skip navigation file
    if (file == "NAVIGATION.md"):
      continue
    # These files don't display correctly; make them a download 
    dot = file.rfind('.')
    if (((file != "Makefile" and file != "SConscript") and dot == -1) or 
        (file[dot:] == ".bib") or
        (file[dot:] == ".gz") or 
        (file[dot:] == ".dtb")):
      # Copy the file over to the assets folder (unfortunately, can't just leave it in the includes folder)
      asset_path = pathlib.Path(f"{full_dir_path}/{file}".replace("workspace_pages", "assets/workspace"))
      if (not os.path.exists(asset_path)):
        # Make directory path
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        # Copy
        shutil.copy(src = pathlib.Path(f"{root}/{file}"), dst = asset_path)
        print(f"Copied asset file for {asset_path}")

      contents = ("\nThis file type does not display properly; you may download it instead: "
        f"[`{file}`](/{asset_path})\n")

    # Otherwise, display them as a code block
    else:
      syntax = "txt"
      if file == "Makefile":
        syntax = "make"
      elif file == "SConscript":
        syntax = "python"
      else:
        ext = file[file.rfind('.'):]
        if syntax_highlights.__contains__(ext):
          syntax = syntax_highlights[ext]

      contents = (f"\n```{syntax}"
        f"\n{{% include {root.removeprefix('_includes/')}/{file} %}}\n"
        "```\n"
      )

    count += 1

    # Make and write to the file
    file_path = f"{full_dir_path}/{filename}"
    if not os.path.exists(file_path):
      # Make and write to the file
      with open(file_path, 'w', encoding="utf-8") as code_file:
        code_file.write(f"{front_matter}{contents}")
      print(f"Made code file for {file_path}")
  