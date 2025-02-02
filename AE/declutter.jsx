// Declutter Script
// A script to organize After Effects project assets into a hierarchical structure

(function(thisObj) {
    // BUILD UI
    var win = (thisObj instanceof Panel) ? thisObj : new Window("palette", "Declutter", undefined);
    win.orientation = "column";
    win.alignChildren = ["center", "top"];
    win.spacing = 10;
    win.margins = 16;

    var logoText = win.add("statictext", undefined, "Declutter");
    logoText.alignment = ["center", "center"];
    logoText.characters = 20;
    logoText.font = ScriptUI.newFont("Arial", "BOLD", 14);

    var descText = win.add("statictext", undefined, "Organize project assets into folders", {multiline: true});
    descText.alignment = ["center", "center"];
    descText.characters = 30;

    var btnOrganize = win.add("button", undefined, "Organize Project");
    btnOrganize.size = [120, 30];
    
    btnOrganize.onClick = function() {
        declutter();
    }

    win.center();
    win.show();

    function declutter() {
        app.beginUndoGroup("Declutter Project");
        
        var project = app.project;
        var rootFolder = project.rootFolder;
        
        // Initialize counters for different types
        var counts = {
            comps: 0,
            precomps: 0,
            audio: {},
            video: {},
            images: {},
            sequences: 0,
            data: {},
            solids: 0
        };

        // First pass: count items
        for (var i = 1; i <= project.numItems; i++) {
            var item = project.item(i);
            if (item instanceof FolderItem) continue;

            if (item instanceof CompItem) {
                if (isPrecomp(item)) {
                    counts.precomps++;
                } else {
                    counts.comps++;
                }
            } else if (item instanceof FootageItem) {
                countFootage(item, counts);
            }
        }

        // Create only needed folders
        var folders = {};
        
        // Create composition folders if needed
        if (counts.comps > 0 || counts.precomps > 0) {
            folders.comps = createFolder("Compositions", 9);
            
            // Create precomps as a subfolder if needed
            if (counts.precomps > 0) {
                folders.precomps = createFolder("Pre-compositions", 5, folders.comps);
            }
        }

        // Create media folder only if needed
        var hasMedia = hasAnyMedia(counts);
        if (hasMedia) {
            folders.media = createFolder("Media", 13);
            
            // Create media subfolders only if needed
            folders.mediaSub = {};
            
            if (hasKeys(counts.audio)) {
                folders.mediaSub.audio = createMediaSubfolders(folders.media, "Audio", counts.audio);
            }
            if (hasKeys(counts.video)) {
                folders.mediaSub.video = createMediaSubfolders(folders.media, "Video", counts.video);
            }
            if (hasKeys(counts.images)) {
                folders.mediaSub.images = createMediaSubfolders(folders.media, "Images", counts.images);
            }
            if (counts.sequences > 0) {
                folders.mediaSub.sequences = createFolder("Sequences", 7, folders.media);
            }
        }

        // Create solids folder if needed
        if (counts.solids > 0 && !folders.solids) {
            folders.solids = createFolder("Solids", 2);
        }

        // Create data folder if needed
        if (hasKeys(counts.data)) {
            folders.data = createFolder("Data", 6);
            folders.dataSub = createMediaSubfolders(folders.data, "Data", counts.data);
        }

        // Second pass: organize items
        for (var i = 1; i <= project.numItems; i++) {
            var item = project.item(i);
            if (item instanceof FolderItem) continue;

            try {
                if (item instanceof CompItem) {
                    handleComposition(item, folders);
                } else if (item instanceof FootageItem) {
                    handleFootage(item, folders);
                }
            } catch (e) {
                alert("Error processing " + item.name + ": " + e.toString());
            }
        }

        app.endUndoGroup();
        alert("Project organized successfully!");
    }

    function isPrecomp(comp) {
        // Check if this comp is used as a layer in any other comp
        for (var i = 1; i <= app.project.numItems; i++) {
            var item = app.project.item(i);
            if (item instanceof CompItem && item !== comp) {
                for (var j = 1; j <= item.numLayers; j++) {
                    var layer = item.layer(j);
                    if (layer.source === comp) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    function handleComposition(comp, folders) {
        // Check if this comp is used in other comps
        var targetFolder = isPrecomp(comp) ? folders.precomps : folders.comps;
        if (targetFolder) {
            comp.parentFolder = targetFolder;
        }
    }

    function countFootage(footage, counts) {
        if (footage.mainSource instanceof SolidSource) {
            counts.solids++;
            return;
        }

        var file = footage.mainSource.file;
        if (!file) return;

        var ext = file.name.split('.').pop().toUpperCase();

        if (footage.mainSource.isSequence) {
            counts.sequences++;
        } else if (contains(["WAV","MP3","AAC","AIFF"], ext)) {
            counts.audio[ext] = (counts.audio[ext] || 0) + 1;
        } else if (contains(["MP4","MOV","AVI","R3D","BRAW"], ext)) {
            counts.video[ext] = (counts.video[ext] || 0) + 1;
        } else if (contains(["JPG","JPEG","PNG","PSD","AI","TIFF","TIF"], ext)) {
            counts.images[ext] = (counts.images[ext] || 0) + 1;
        } else if (contains(["JSON","CSV","PDF","TXT","XML","XLSX"], ext)) {
            counts.data[ext] = (counts.data[ext] || 0) + 1;
        }
    }

    function handleFootage(footage, folders) {
        if (footage.mainSource instanceof SolidSource) {
            if (folders.solids) footage.parentFolder = folders.solids;
            return;
        }

        var file = footage.mainSource.file;
        if (!file) return;

        var ext = file.name.split('.').pop().toUpperCase();
        
        if (footage.mainSource.isSequence && folders.mediaSub && folders.mediaSub.sequences) {
            footage.parentFolder = folders.mediaSub.sequences;
        } else if (folders.mediaSub) {
            var subfolder = null;
            if (contains(["WAV","MP3","AAC","AIFF"], ext) && folders.mediaSub.audio) {
                subfolder = getSubfolderByExtension(folders.mediaSub.audio, ext);
            } else if (contains(["MP4","MOV","AVI","R3D","BRAW"], ext) && folders.mediaSub.video) {
                subfolder = getSubfolderByExtension(folders.mediaSub.video, ext);
            } else if (contains(["JPG","JPEG","PNG","PSD","AI","TIFF","TIF"], ext) && folders.mediaSub.images) {
                subfolder = getSubfolderByExtension(folders.mediaSub.images, ext);
            }
            
            if (subfolder) footage.parentFolder = subfolder;
        }
    }

    function createFolder(name, labelColor, parent) {
        var folder = (parent || app.project).items.addFolder(name);
        folder.label = labelColor;
        if (parent) {
            folder.parentFolder = parent;
        }
        return folder;
    }

    function createMediaSubfolders(parent, category, typeCount) {
        var folder = createFolder(category, getColorForCategory(category), parent);
        var subfolders = {};
        for (var type in typeCount) {
            if (typeCount[type] > 0) {
                subfolders[type.toLowerCase()] = createFolder(type, 0, folder);
            }
        }
        return folder;
    }

    function getSubfolderByExtension(parentFolder, ext) {
        var subfolderName = ext.toUpperCase();
        var existing = null;
        
        for (var i = 1; i <= parentFolder.items.length; i++) {
            if (parentFolder.items[i].name === subfolderName) {
                existing = parentFolder.items[i];
                break;
            }
        }
        
        return existing || createFolder(subfolderName, 0, parentFolder);
    }

    function getColorForCategory(category) {
        var colors = {
            "Audio": 11,    // Green
            "Video": 13,    // Dark Blue
            "Images": 3,    // Red
            "Documents": 4, // Brown
            "Code": 6,     // Orange
            "Sequences": 7  // Blue
        };
        return colors[category] || 0;
    }

    // Helper functions
    function contains(arr, item) {
        for (var i = 0; i < arr.length; i++) {
            if (arr[i] === item) return true;
        }
        return false;
    }

    function hasKeys(obj) {
        for (var key in obj) {
            if (obj[key] > 0) return true;
        }
        return false;
    }

    function hasAnyMedia(counts) {
        return hasKeys(counts.audio) || 
               hasKeys(counts.video) || 
               hasKeys(counts.images) || 
               counts.sequences > 0;
    }

})(this);
