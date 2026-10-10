import os
import pathlib

#
# A painfully human-written helper script to turn add workspace folder files to the site
#

# Helper: workspace file/dir name to website file/dir name
def work_name_to_web_name(work_name, unit):
  first_hyphen = work_name.find('-')

  if first_hyphen != 2:
    # completed folder -> completed folder
    if work_name == "complete" or work_name == "completed":
      return("completed")
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

# Helper: find prefix
def web_has_unit(web_dirs, dir_num):
  for dir in web_dirs:
    if dir[0:dir.find('-')] == dir_num:
      return True
  return False

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

def unit_num(name):
   return name[0:name.find('-')]

unit_titles = ["Unit I: Introduction", "Unit II: Beginning Simulation", "Unit III: Intermediate Features", "Unit IV: Developing gem5 Models", "Unit V: Advanced Topics"]
track_titles = {"04a": "Track 1: Processors", 
                "04b": "Track 2: Caches", 
                "04c": "Track 3: Memory"}
sections = {"01-01" : "Section 1: Why simulation?",
            "01-02" : "Section 2: Enter gem5",
            "01-03" : "Section 3: Installing gem5",
            "01-04" : "Section 4: Your First configuration script",
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

syntax_highlights = {".py" : "python",
                     ".cc" : "cpp",
                     ".c" : "c",
                     ".txt" : "txt",
                     ".json" : "json",
                     ".hh" : "cpp",
                     ".h" : "c"
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
      filepath = f"{curr_web_root}/{curr_section_dir}"
      file_name = work_name_to_web_name(path_name, unit_num(curr_unit_dir))
      # The wild west of subdirectories!
      # One special case: are we looking right at the "completed" directory?
      # If so, it has a different parent in the front matter and needs to be handled separately
      if (file_name == "completed"):
        file_title = f"{curr_section_dir[curr_section_dir.find('/') + 1 :]} Completed Files"
        parent_web_names[path] = file_title
        # Create front matter
        front_matter = ("---\n"
                f"title: \"{file_title}\"\n"
                f"parent: \"{sections[filepath[filepath.rfind('/') + 1:]]}\"\n"
                f"layout: default\n"
                f"nav_order: 2\n"
                "---\n"
                ""
        )
        file_path = f"{filepath}/00-completed.md"
        if not os.path.exists(file_path):
          # Make and write to the file
          with open(file_path, 'w', encoding="utf-8") as comp_file:
            comp_file.write(front_matter)
          print(f"Made completed table-of-contents file for {filepath}/{path_name}")
      # Just normal subdirectory things
      else:
        parent_web_names[path] = path_name
        # Create front matter
        front_matter = ("---\n"
                f"title: \"{path_name}\"\n"
                f"parent: \"{parent_web_names[parent]}\"\n"
                f"layout: default\n"
                f"nav_order: 2\n"
                "---\n"
                ""
        )
        file_path = f"{filepath}/{file_name}"
        if not os.path.exists(file_path):
          # Make and write to the file
          with open(file_path, 'w', encoding="utf-8") as sub_file:
            sub_file.write(front_matter)
          print(f"Made table-of-contents file for {filepath}/{path_name}")

  #
  # FILE HANDLING
  #
  count = 0
  for file in files:
    print(file)
    dot = file.rfind('.')
    if not ((file == "NAVIGATION.md") or 
            (file != "Makefile" and dot == -1) or 
            (file[dot:] == ".bib") or 
            (file[dot:] == ".gz") or 
            (file[dot:] == ".dtb")):
      # Build the front matter
      filename = work_name_to_web_name(file, unit_num(curr_unit_dir))
      if parent_web_names.__contains__(path):
        parent_web_name = parent_web_names[path]
      else:
        parent_web_name = parent_name
      
      front_matter = ("---\n"
                      f"title: \"{file}\"\n"
                      f"parent: \"{parent_web_name}\"\n"
                      f"layout: default\n"
                      f"nav_order: {count}\n"
                      "---\n"
                      ""
      )
      # Build the contents
      syntax = "txt"
      if file == "Makefile":
        syntax = "make"
      else:
        ext = file[file.rfind('.'):]
        if syntax_highlights.__contains__(ext):
          syntax = syntax_highlights[ext]

      contents = (f"```{syntax}\n"
        f"{{% include {root.removeprefix('_includes/')}/{file} %}}\n"
        "```\n"
      )
      count += 1

      # Make and write to the file
      file_path = f"{curr_web_root}/{curr_section_dir}/{filename}"
      if not os.path.exists(file_path):
        # Make and write to the file
        with open(file_path, 'w', encoding="utf-8") as code_file:
          code_file.write(f"{front_matter}{contents}")
        print(f"Made code file for {file_path}")
      


  