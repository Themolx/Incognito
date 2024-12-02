{
    app.beginUndoGroup("Process Project Path and Setup Render Queue");

    function getProjectFolderPath() {
        var projectPath = app.project.file.path;
        alert("Full project path: " + projectPath);
        
        // Split path and look for project token (e.g., BRIT_OOH_02435)
        var pathParts = projectPath.split(/[\\\/]/);
        var projectIndex = -1;
        
        for (var i = 0; i < pathParts.length; i++) {
            if (pathParts[i].match(/[A-Z]+_[A-Z]+_\d+/)) {
                projectIndex = i;
                break;
            }
        }
        
        if (projectIndex === -1) {
            alert("ERROR: Could not find project token in path!");
            return null;
        }
        
        // Reconstruct path up to the project folder
        var projectFolderPath = pathParts.slice(0, projectIndex + 1).join('/');
        alert("Found project folder path: " + projectFolderPath);
        return projectFolderPath;
    }

    function findDailiesFolder(projectFolderPath) {
        // First try to find output/_dailies
        var outputFolder = new Folder(projectFolderPath + "/output");
        
        if (!outputFolder.exists) {
            alert("ERROR: Could not find output folder in: " + projectFolderPath);
            return null;
        }
        
        // Try both variants of dailies folder
        var dailiesWithUnderscore = new Folder(outputFolder.fsName + "/_dailies");
        var dailiesWithoutUnderscore = new Folder(outputFolder.fsName + "/dailies");
        
        alert("Checking for dailies folders:\n" + 
              "With underscore: " + dailiesWithUnderscore.fsName + " (exists: " + dailiesWithUnderscore.exists + ")\n" +
              "Without underscore: " + dailiesWithoutUnderscore.fsName + " (exists: " + dailiesWithoutUnderscore.exists + ")");
        
        if (dailiesWithUnderscore.exists) {
            return dailiesWithUnderscore;
        } else if (dailiesWithoutUnderscore.exists) {
            return dailiesWithoutUnderscore;
        }
        
        return null;
    }

    function createDateFolder(parentFolder) {
        var date = new Date();
        var dateString = date.getFullYear().toString().substr(-2) +
                        ("0" + (date.getMonth() + 1)).slice(-2) +
                        ("0" + date.getDate()).slice(-2);
        
        var newFolder = new Folder(parentFolder.fsName + "/" + dateString);
        alert("Creating date folder: " + newFolder.fsName);
        
        if (!newFolder.exists) {
            var created = newFolder.create();
            alert("Folder creation " + (created ? "successful" : "failed"));
        }
        return newFolder;
    }

    function setupRenderQueue(outputPath) {
        var selectedItems = app.project.selection;
        var comps = [];
        
        alert("Selected items: " + selectedItems.length);
        
        for (var i = 0; i < selectedItems.length; i++) {
            if (selectedItems[i] instanceof CompItem) {
                comps.push(selectedItems[i]);
            }
        }
        
        alert("Found " + comps.length + " compositions to render");
        
        for (var i = 0; i < comps.length; i++) {
            var renderQueueItem = app.project.renderQueue.items.add(comps[i]);
            var outputModule = renderQueueItem.outputModule(1);
            var outputFile = new File(outputPath.fsName + "/" + comps[i].name);
            
            alert("Setting output path for " + comps[i].name + ":\n" + outputFile.fsName);
            outputModule.file = outputFile;
        }
    }

    function main() {
        alert("Script starting...");
        
        // Get project folder path by analyzing current project path
        var projectFolderPath = getProjectFolderPath();
        if (!projectFolderPath) {
            return;
        }
        
        // Find dailies folder within the project structure
        var dailiesFolder = findDailiesFolder(projectFolderPath);
        if (!dailiesFolder) {
            alert("ERROR: Could not find dailies folder in project structure!");
            return;
        }
        
        // Create date folder
        var dateFolder = createDateFolder(dailiesFolder);
        if (!dateFolder) {
            alert("ERROR: Could not create date folder in " + dailiesFolder.fsName);
            return;
        }
        
        // Setup render queue
        setupRenderQueue(dateFolder);
        
        alert("Process complete!\nOutput path: " + dateFolder.fsName);
    }

    main();
    
    app.endUndoGroup();
}
