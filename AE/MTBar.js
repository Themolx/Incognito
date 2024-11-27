// MTBar.jsx
// Script panel for running After Effects scripts
// Written by Martin Tomek

(function(thisObj) {
    // Build UI
    function buildUI(thisObj) {
        var DEFAULT_SCRIPTS_PATH = "/Users/martintomek/Downloads/Incognito-main/AE";
        alert("MTBar starting...\nLooking for scripts in: " + DEFAULT_SCRIPTS_PATH);
        
        var win = (thisObj instanceof Panel) ? thisObj : new Window("palette", "MTBar", undefined, {resizeable: true, closeButton: true});
        win.orientation = "column";
        win.alignChildren = ["fill", "top"];
        win.spacing = 4;
        win.margins = 16;

        // Header with refresh button
        var headerGroup = win.add("group");
        headerGroup.orientation = "row";
        headerGroup.alignChildren = ["left", "center"];
        headerGroup.spacing = 10;
        
        var titleText = headerGroup.add("statictext", undefined, "MTBar");
        titleText.graphics.font = ScriptUI.newFont("Arial", "BOLD", 14);
        
        var refreshBtn = headerGroup.add("button", undefined, "Refresh");
        refreshBtn.helpTip = "Refresh script list";
        refreshBtn.preferredSize.width = 70;

        // Styles
        var btnStyle = {
            preferredSize: [200, 30],
            fill: [0.2, 0.2, 0.2],
            stroke: [0.8, 0.8, 0.8],
            font: "Arial-Bold:12",
            justify: "left",
            margins: 10
        };

        // Scripts panel with scrollbar
        var scriptsPanel = win.add("panel", undefined, "Scripts");
        scriptsPanel.orientation = "column";
        scriptsPanel.alignChildren = ["fill", "top"];
        scriptsPanel.spacing = 4;
        scriptsPanel.margins = 10;

        // Create scrollable list
        var listGroup = scriptsPanel.add("group");
        listGroup.orientation = "column";
        listGroup.alignChildren = ["fill", "top"];
        listGroup.spacing = 4;
        listGroup.maximumSize.height = 400; // Limit height for scrolling

        // Store references
        var scriptButtons = [];
        var currentFolder = DEFAULT_SCRIPTS_PATH;

        // Helper function to check file extension
        function hasScriptExtension(filename) {
            filename = filename.toLowerCase();
            return filename.substr(-3) === '.js' || filename.substr(-4) === '.jsx';
        }

        // Function to refresh script buttons
        function refreshScriptButtons() {
            // Remove existing buttons
            for (var i = 0; i < scriptButtons.length; i++) {
                if (scriptButtons[i] && scriptButtons[i].parent) {
                    scriptButtons[i].parent.remove(scriptButtons[i]);
                }
            }
            scriptButtons = [];

            if (currentFolder) {
                var folder = new Folder(currentFolder);
                alert("Checking folder: " + folder.fsName + "\nExists: " + folder.exists);
                
                if (!folder.exists) {
                    alert("Scripts folder does not exist: " + currentFolder);
                    return;
                }

                // Get both .js and .jsx files
                var files = folder.getFiles(function(file) {
                    return file instanceof File && hasScriptExtension(file.name);
                });
                
                alert("Found " + files.length + " script files");
                
                // Sort files alphabetically
                files.sort(function(a, b) {
                    return a.displayName.toLowerCase() < b.displayName.toLowerCase() ? -1 : 1;
                });
                
                // Add test button first
                var testBtn = listGroup.add("button", undefined, "Run Test Script");
                testBtn.onClick = function() {
                    alert("Button clicked!");
                    try {
                        var testScript = new File(currentFolder + "/test.jsx");
                        alert("Test script exists: " + testScript.exists);
                        $.evalFile(testScript);
                    } catch (e) {
                        alert("Error running test script: " + e.toString());
                    }
                };
                scriptButtons.push(testBtn);
                
                // Add other script buttons
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];
                    // Skip this script
                    if (file.name === "MTBar.jsx") continue;
                    
                    var btn = listGroup.add("button", undefined, file.displayName);
                    btn.file = file;
                    
                    // Apply style
                    for (var prop in btnStyle) {
                        btn[prop] = btnStyle[prop];
                    }
                    
                    btn.onClick = function() {
                        alert("Running script: " + this.file.fsName);
                        try {
                            $.evalFile(this.file);
                        } catch (e) {
                            alert("Error running script: " + e.toString());
                        }
                    };
                    
                    scriptButtons.push(btn);
                }

                if (scriptButtons.length <= 1) { // Only test button
                    var noScriptsLabel = listGroup.add("statictext", undefined, "No .js/.jsx files found");
                    scriptButtons.push(noScriptsLabel);
                }
            }
            
            win.layout.layout(true);
        }

        // Add refresh button handler
        refreshBtn.onClick = function() {
            refreshScriptButtons();
        };

        // Make panel resizable
        win.onResizing = win.onResize = function() {
            this.layout.resize();
        };

        // Show the window
        if (win instanceof Window) {
            win.center();
            win.show();
        } else {
            win.layout.layout(true);
        }

        // Load scripts immediately
        refreshScriptButtons();
    }

    buildUI(thisObj);

})(this);
