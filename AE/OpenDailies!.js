/*
Open Today's Dailies Folder Script
This script:
1. Finds project folder path based on project token pattern
2. Locates dailies folder in project structure or output folder
3. Creates date-based folder if it doesn't exist
4. Opens the folder in File Explorer
*/

{
    // User configurable variables
    var DEBUG_MODE = false; // Enable detailed debugging

    function debugLog(message) {
        if (DEBUG_MODE) {
            alert("🔍 DEBUG: " + message);
        }
    }

    function getProjectFolderPath() {
        var projectPath = app.project.file.path;
        debugLog("RAW PATH: " + projectPath);
        
        var pathParts = projectPath.split(/[\\\/]/);
        for (var i = 0; i < pathParts.length; i++) {
            debugLog("Part " + i + ": [" + pathParts[i] + "]");
        }
        
        if (pathParts.length < 3) {
            alert("ERROR: Path is too short to extract mapping and project token!");
            return null;
        }
        
        var drive = pathParts[1];
        var project = pathParts[2];
        
        debugLog("DRIVE BEFORE: [" + drive + "]");
        debugLog("PROJECT: [" + project + "]");

        drive = drive.charAt(0).toUpperCase();
        debugLog("DRIVE LETTER: [" + drive + "]");

        var projectFolderPath = drive + ":\\" + project;
        debugLog("FINAL PATH: [" + projectFolderPath + "]");
        
        return projectFolderPath;
    }

    function findDailiesFolder(projectFolderPath) {
        debugLog("LOOKING FOR DAILIES IN: [" + projectFolderPath + "]");
        
        var dailiesVariants = ["_dailies", "dailies", "_Dailies", "Dailies"];
        var searchPaths = [
            projectFolderPath,                    // Check in project root
            projectFolderPath + "\\output"        // Check in output folder
        ];
        
        debugLog("Checking in paths: " + JSON.stringify(searchPaths));
        
        for (var pathIndex = 0; pathIndex < searchPaths.length; pathIndex++) {
            var basePath = searchPaths[pathIndex];
            debugLog("Checking base path: [" + basePath + "]");
            
            for (var i = 0; i < dailiesVariants.length; i++) {
                var dailiesPath = basePath + "\\" + dailiesVariants[i];
                debugLog("TRYING: [" + dailiesPath + "]");
                
                var currentFolder = new Folder(dailiesPath);
                debugLog("EXISTS? " + currentFolder.exists);
                
                if (currentFolder.exists) {
                    debugLog("FOUND IT!: " + dailiesPath);
                    return currentFolder;
                }
            }
        }
        
        alert("ERROR: No dailies folder found in project or output folder!");
        return null;
    }

    function padNumber(number, width) {
        number = number.toString();
        while (number.length < width) {
            number = "0" + number;
        }
        return number;
    }

    function getTodayFolder(dailiesFolder) {
        var date = new Date();
        var dateString = date.getFullYear().toString().substr(-2) +
                        padNumber(date.getMonth() + 1, 2) +
                        padNumber(date.getDate(), 2);
        return new Folder(dailiesFolder.fsName + "\\" + dateString);
    }

    function openInExplorer(folder) {
        if (folder.exists) {
            folder.execute();
        } else {
            folder.create();
            folder.execute();
        }
    }

    function main() {
        var projectFolder = getProjectFolderPath();
        if (!projectFolder) return;

        var dailiesFolder = findDailiesFolder(projectFolder);
        if (!dailiesFolder) return;

        var todayFolder = getTodayFolder(dailiesFolder);
        openInExplorer(todayFolder);
    }

    main();
}
