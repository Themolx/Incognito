/* 
    Batch Renamer for After Effects
    --------------------------------
    This script creates a UI that lets you batch rename selected compositions in the Project panel.
    It allows you to:
      • Find and replace text in comp names.
      • Add a prefix and/or a suffix.
      • Optionally, process nested comps (i.e. any comp referenced as a layer source).
    
    To use:
      1. Select one or more compositions in the Project panel.
      2. Run the script.
      3. Enter your renaming parameters and click "Rename".
*/

{
    // Make sure a project exists.
    if (!app.project) {
        alert("Please open a project first.");
        return;
    }

    // Create the UI palette window.
    var win = new Window("palette", "Batch Renamer", undefined, {resizeable: true});
    win.orientation = "column";
    win.alignChildren = ["fill", "top"];
    win.spacing = 10;
    win.margins = 16;

    // Find/Replace Group
    var findGroup = win.add("group");
    findGroup.orientation = "row";
    findGroup.alignChildren = ["left", "center"];
    findGroup.add("statictext", undefined, "Find:");
    var findField = findGroup.add("edittext", undefined, "");
    findField.characters = 20;

    var replaceGroup = win.add("group");
    replaceGroup.orientation = "row";
    replaceGroup.alignChildren = ["left", "center"];
    replaceGroup.add("statictext", undefined, "Replace:");
    var replaceField = replaceGroup.add("edittext", undefined, "");
    replaceField.characters = 20;

    // Prefix/Suffix Group
    var prefixGroup = win.add("group");
    prefixGroup.orientation = "row";
    prefixGroup.alignChildren = ["left", "center"];
    prefixGroup.add("statictext", undefined, "Prefix:");
    var prefixField = prefixGroup.add("edittext", undefined, "");
    prefixField.characters = 20;

    var suffixGroup = win.add("group");
    suffixGroup.orientation = "row";
    suffixGroup.alignChildren = ["left", "center"];
    suffixGroup.add("statictext", undefined, "Suffix:");
    var suffixField = suffixGroup.add("edittext", undefined, "");
    suffixField.characters = 20;

    // Checkbox: Process nested comps?
    var nestedCheckbox = win.add("checkbox", undefined, "Process Nested Comps");
    nestedCheckbox.value = true; // default to processing nested comps

    // Button Group: Rename and Cancel
    var buttonGroup = win.add("group");
    buttonGroup.alignment = "center";
    var renameBtn = buttonGroup.add("button", undefined, "Rename");
    var cancelBtn = buttonGroup.add("button", undefined, "Cancel");

    // Recursive function to rename a composition and (if enabled) any nested comps.
    function renameComp(compItem, findStr, replaceStr, prefix, suffix, processNested) {
        // Get the original name.
        var oldName = compItem.name;
        var newName = oldName;

        // If a find string was provided, do a global find & replace.
        if (findStr !== "") {
            // Simple method using split/join for global replacement.
            newName = newName.split(findStr).join(replaceStr);
        }

        // Add prefix and suffix.
        newName = prefix + newName + suffix;

        // Set the new name.
        compItem.name = newName;

        // Process nested comps if enabled.
        if (processNested && compItem.layers) {
            for (var i = 1; i <= compItem.layers.length; i++) {
                var layer = compItem.layers[i];
                // Check if the layer has a source and if that source is a composition.
                if (layer.source && (layer.source instanceof CompItem)) {
                    renameComp(layer.source, findStr, replaceStr, prefix, suffix, processNested);
                }
            }
        }
    }

    // When the "Rename" button is clicked...
    renameBtn.onClick = function() {
        // Wrap changes in an undo group.
        app.beginUndoGroup("Batch Rename Comps");

        // Retrieve values from the UI fields.
        var findStr     = findField.text;
        var replaceStr  = replaceField.text;
        var prefix      = prefixField.text;
        var suffix      = suffixField.text;
        var processNested = nestedCheckbox.value;

        // Get the selected items from the Project panel.
        var items = app.project.selection;
        if (!items || items.length === 0) {
            alert("Please select at least one composition in the Project panel.");
            app.endUndoGroup();
            return;
        }

        // Loop through the selection and process only compositions.
        for (var i = 0; i < items.length; i++) {
            if (items[i] instanceof CompItem) {
                renameComp(items[i], findStr, replaceStr, prefix, suffix, processNested);
            }
        }

        app.endUndoGroup();
        alert("Rename operation completed.");
    };

    // Close the window if "Cancel" is clicked.
    cancelBtn.onClick = function() {
        win.close();
    };

    // Show the UI.
    win.center();
    win.show();
}
