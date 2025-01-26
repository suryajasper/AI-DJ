using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(DJ))]
public class DJEditorManager : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();

        DJ manager = (DJ)target;
        if (GUILayout.Button("Trigger Pick Up Animation"))
        {
            manager.PlayPickUpAnimation();
        }
    }
}