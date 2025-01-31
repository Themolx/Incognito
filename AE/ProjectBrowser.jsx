{
    // ProjectBrowser.jsx
    // Script to browse and open After Effects projects
    
    function ProjectBrowser() {
        // Create the main window
        var mainWindow = new Window("palette", "AE Project Browser", undefined);
        mainWindow.orientation = "column";
        mainWindow.alignChildren = ["fill", "fill"];
        mainWindow.spacing = 10;
        mainWindow.margins = 16;

        // Function to get all week folders from the year directory
        function getWeekFolders() {
            var yearPath = "P:/KAUF_2025_02009/Shots";
            var yearFolder = new Folder(yearPath);
            var folders = [];
            
            if (yearFolder.exists) {
                var allItems = yearFolder.getFiles();
                for (var i = 0; i < allItems.length; i++) {
                    if (allItems[i] instanceof Folder) {
                        // Check if folder name starts with 'ww'
                        if (allItems[i].name.toLowerCase().indexOf('ww') === 0) {
                            folders.push(allItems[i].name);
                        }
                    }
                }
                // Sort by week number (extract number after 'ww')
                folders.sort(function(a, b) {
                    var numA = parseInt(a.toLowerCase().replace('ww', ''));
                    var numB = parseInt(b.toLowerCase().replace('ww', ''));
                    return numB - numA; // Sort in descending order
                });
            }
            return folders;
        }

        // Function to get current week from active project
        function getCurrentWeek() {
            var currentProject = app.project.file;
            if (currentProject) {
                var pathParts = currentProject.fsName.split(/[\/\\]/); // Split by both forward and backward slashes
                if (pathParts.length >= 4) {
                    return pathParts[3]; // This will be the week folder (e.g., 'ww07')
                }
            }
            return null;
        }

        // Add navigation controls
        var navGroup = mainWindow.add("group");
        navGroup.orientation = "row";
        navGroup.alignChildren = ["left", "center"];
        
        var weekLabel = navGroup.add("statictext", undefined, "Week:");
        var weekDropdown = navGroup.add("dropdownlist", undefined, getWeekFolders());
        weekDropdown.preferredSize.width = 100;
        
        // Try to select current week, if not found select the highest week (first in the sorted list)
        var currentWeek = getCurrentWeek();
        if (currentWeek && weekDropdown.find(currentWeek)) {
            weekDropdown.selection = weekDropdown.find(currentWeek);
        } else if (weekDropdown.items.length > 0) {
            // Select the first item (which will be the highest week due to our sorting)
            weekDropdown.selection = 0;
        }

        // Add checkbox for latest versions
        var showLatestCheckbox = mainWindow.add("checkbox", undefined, "Show only latest versions");
        showLatestCheckbox.value = true; // Checked by default
        
        // Create a list box to show projects
        var projectList = mainWindow.add("listbox", undefined, [], {
            multiselect: false
        });
        projectList.preferredSize.width = 400;
        projectList.preferredSize.height = 300;
        
        // Add double-click handler
        projectList.onDoubleClick = openSelectedProject;
    
        // Add buttons panel
        var buttonGroup = mainWindow.add("group");
        buttonGroup.orientation = "row";
        buttonGroup.alignChildren = ["center", "center"];
        
        var refreshBtn = buttonGroup.add("button", undefined, "Refresh");
        var openBtn = buttonGroup.add("button", undefined, "Open Project");
    
        // Function to get current folder path
        function getCurrentFolderPath() {
            if (weekDropdown.selection) {
                return "P:/KAUF_2025_02009/Shots/" + weekDropdown.selection.text;
            }
            return null;
        }

        // Function to scan for AE projects
        function scanForProjects() {
            projectList.removeAll(); // Clear existing items
            
            var folderPath = getCurrentFolderPath();
            if (!folderPath) {
                alert("Please select a week from the dropdown!");
                return;
            }

            var folder = new Folder(folderPath);
            if (folder.exists) {
                var files = folder.getFiles("*.aep");
                
                // Group files by base name (without version)
                var projectGroups = {};
                for (var i = 0; i < files.length; i++) {
                    var fileName = files[i].displayName;
                    // Match pattern: anything followed by _v or V and numbers (e.g., "project_v001.aep" or "project_V02.aep")
                    var match = fileName.match(/(.*?)(?:[_.]v|V)(\d+)/i);
                    
                    if (match) {
                        var baseName = match[1];
                        var version = parseInt(match[2], 10);
                        
                        if (!projectGroups[baseName]) {
                            projectGroups[baseName] = [];
                        }
                        projectGroups[baseName].push({
                            fileName: fileName,
                            version: version
                        });
                    } else {
                        // Files without version number are treated as individual groups
                        projectGroups[fileName] = [{
                            fileName: fileName,
                            version: 0
                        }];
                    }
                }
                
                // Add files to the list based on checkbox state
                for (var baseName in projectGroups) {
                    var projects = projectGroups[baseName];
                    
                    if (showLatestCheckbox.value) {
                        // Sort by version and add only the highest version
                        projects.sort(function(a, b) {
                            return b.version - a.version;
                        });
                        projectList.add("item", projects[0].fileName);
                    } else {
                        // Add all versions
                        for (var j = 0; j < projects.length; j++) {
                            projectList.add("item", projects[j].fileName);
                        }
                    }
                }
            } else {
                alert("Folder not found!");
            }
        }
    
        // Function to open selected project
        function openSelectedProject() {
            if (projectList.selection !== null) {
                var folderPath = getCurrentFolderPath();
                if (!folderPath) {
                    alert("Please select a week folder!");
                    return;
                }
                
                var projectPath = folderPath + "/" + projectList.selection.text;
                var projectFile = new File(projectPath);
                if (projectFile.exists) {
                    app.open(projectFile);
                } else {
                    alert("Project file not found!");
                }
            } else {
                alert("Please select a project to open!");
            }
        }
    
        // Event handlers
        refreshBtn.onClick = scanForProjects;
        openBtn.onClick = openSelectedProject;
        showLatestCheckbox.onClick = scanForProjects; // Refresh list when checkbox changes
        weekDropdown.onChange = scanForProjects; // Refresh list when week changes
        
        // Initial scan
        scanForProjects();
    
        return mainWindow;
    }
    
    // Create and show the UI
    var myWindow = ProjectBrowser();
    myWindow.center();
    myWindow.show();
}
