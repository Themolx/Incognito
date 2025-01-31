// SoundImporter.jsx
// Script to automatically import sound files for AE projects

function importSound() {
    // Function to get project info from path
    function getProjectInfo(projectPath) {
        var pathParts = projectPath.split(/[\/\\]/);
        var projectFileName = pathParts[pathParts.length - 1];

        // Find the year and week tokens
        var year = "";
        var week = "";

        // Look specifically for week in the fourth token (index 3)
        if (pathParts.length > 3 && pathParts[3].match(/^ww\d+$/i)) {
            week = pathParts[3];
        }

        // Find year token anywhere in the path
        for (var i = 0; i < pathParts.length; i++) {
            if (pathParts[i].match(/KAUF_\d{4}/)) {
                year = pathParts[i];
                break;
            }
        }

        return {
            year: year,
            week: week,
            projectName: projectFileName.replace('.aep', '')
        };
    }

    // Function to find the sound folder
    function findSoundFolder(projectInfo) {
        if (!projectInfo.year || !projectInfo.week) {
            alert("Missing year or week information!");
            return null;
        }

        var soundBasePath = "P:/" + projectInfo.year + "/ZADANI/" + projectInfo.week + "/sound/od_zvukare";
        var soundFolder = new Folder(soundBasePath);
        
        if (!soundFolder.exists) return null;

        // Find the "Full Mix" folder
        var fullMixFolders = soundFolder.getFiles(function(file) {
            var decodedName = decodeURI(file.name);
            return file instanceof Folder && decodedName.toLowerCase().indexOf("full mix") !== -1;
        });

        return fullMixFolders.length > 0 ? fullMixFolders[0] : null;
    }

    // Function to find matching project folder
    function findProjectFolder(fullMixFolder, projectName) {
        if (!fullMixFolder) return null;

        var projectFolders = fullMixFolder.getFiles(function(file) {
            return file instanceof Folder;
        });

        var bestMatch = null;
        var bestMatchScore = 0;
        var projectParts = projectName.toLowerCase().split(/[_\s]/);

        for (var i = 0; i < projectFolders.length; i++) {
            var folder = projectFolders[i];
            var decodedName = decodeURI(folder.name);
            var score = 0;
            var folderWords = decodedName.toLowerCase().split(/[_\s]/);

            for (var j = 0; j < projectParts.length; j++) {
                if (folderWords.indexOf(projectParts[j]) !== -1) {
                    score++;
                }
            }

            if (score > bestMatchScore) {
                bestMatchScore = score;
                bestMatch = folder;
            }
        }

        return bestMatch;
    }

    // Function to find LUFS file
    function findLUFSFile(projectFolder) {
        if (!projectFolder) return null;

        var audioFolder = new Folder(projectFolder.fsName + "/Audio 24bit_48kHz");
        if (!audioFolder.exists) {
            audioFolder = new Folder(projectFolder.fsName + "/FullMix_24bit_48kHz");
        }
        
        if (!audioFolder.exists) return null;

        var lufsFiles = audioFolder.getFiles(function(file) {
            var decodedName = decodeURI(file.name);
            return file instanceof File && 
                   decodedName.toLowerCase().indexOf("lufs") !== -1 && 
                   decodedName.toLowerCase().indexOf(".wav") !== -1;
        });

        return lufsFiles.length > 0 ? lufsFiles[0] : null;
    }

    // Function to find matching composition
    function findMatchingComposition(projectName) {
        // Remove version number from project name (e.g., _v1, _v2, etc.)
        var baseProjectName = projectName.replace(/_v\d+$/, '');
        
        // Look through all items in project
        for (var i = 1; i <= app.project.numItems; i++) {
            var item = app.project.item(i);
            if (item instanceof CompItem) {
                // Remove version number from comp name
                var compName = item.name.replace(/_v\d+$/, '');
                if (compName === baseProjectName) {
                    return item;
                }
            }
        }
        return null;
    }

    // Function to find or create folder in project
    function findOrCreateFolder(folderName) {
        // Look for existing folder
        for (var i = 1; i <= app.project.numItems; i++) {
            var item = app.project.item(i);
            if (item instanceof FolderItem && item.name === folderName) {
                return item;
            }
        }
        
        // Create new folder if not found
        return app.project.items.addFolder(folderName);
    }

    // Function to handle existing audio layers
    function handleExistingAudioLayers(comp) {
        // Create Placeholder Sound folder
        var placeholderFolder = findOrCreateFolder("Placeholder Sound");
        
        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            
            // Check if layer has audio
            if (layer.hasAudio && !layer.audioEnabled) {
                continue; // Skip if audio is already disabled
            }
            
            if (layer.hasAudio) {
                // Set layer color to blue
                layer.label = 9; // Blue label color
                
                // Add marker with "Placeholder sound" comment
                var newMarker = new MarkerValue("Placeholder sound");
                layer.marker.setValueAtTime(0, newMarker);
                
                // Move source to Placeholder Sound folder
                if (layer.source && layer.source.parentFolder !== placeholderFolder) {
                    layer.source.parentFolder = placeholderFolder;
                }
                
                // Disable audio
                layer.audioEnabled = false;
            }
        }
    }

    // Main execution
    if (!app.project.file) {
        alert("Please save your project first!");
        return;
    }

    var projectInfo = getProjectInfo(app.project.file.fsName);
    var fullMixFolder = findSoundFolder(projectInfo);
    
    if (!fullMixFolder) {
        alert("Could not find Full Mix folder!");
        return;
    }

    var projectFolder = findProjectFolder(fullMixFolder, projectInfo.projectName);
    if (!projectFolder) {
        alert("Could not find matching project folder!");
        return;
    }

    var lufsFile = findLUFSFile(projectFolder);
    if (!lufsFile) {
        alert("Could not find LUFS WAV file!");
        return;
    }

    try {
        // Create week folder
        var weekFolder = findOrCreateFolder(projectInfo.week);
        
        // Import to project in the week folder
        var importOptions = new ImportOptions(lufsFile);
        var audioItem = app.project.importFile(importOptions);
        audioItem.parentFolder = weekFolder;
        
        // Find matching composition
        var targetComp = findMatchingComposition(projectInfo.projectName);
        if (targetComp) {
            // Handle existing audio layers first
            handleExistingAudioLayers(targetComp);
            
            // Add to matching composition
            var audioLayer = targetComp.layers.add(audioItem);
            
            // Move audio layer to the top (index 1)
            while (audioLayer.index > 1) {
                audioLayer.moveBefore(targetComp.layer(audioLayer.index - 1));
            }
            
            // Set start time to 0
            audioLayer.startTime = 0;
            
            alert("Successfully imported sound file into composition: " + targetComp.name);
        } else {
            alert("Successfully imported sound file to project! (No matching composition found)");
        }
    } catch (error) {
        alert("Error importing file: " + error.toString());
    }
}

// Execute immediately
importSound();
