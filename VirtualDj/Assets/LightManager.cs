using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class LightManager : MonoBehaviour
{
    public List<Light> lights; // Assign lights in the Inspector
    [Range(1, 5)]
    public int speed = 3; // Flickering speed (1 = slow, 5 = fast)
    public float minIntensity = 0.2f; // Minimum brightness
    public float maxIntensity = 2.0f; // Maximum brightness
    public float rotationSpeed = 30f; // Speed of rotation in degrees per second
    public float multiplier = 0.3f;

    private float[] timeOffsets; // Unique time offsets for each light
    private Vector3[] rotationAxes; // Unique rotation axes for each light

    void Start()
    {
        int lightCount = lights.Count;
        timeOffsets = new float[lightCount];
        rotationAxes = new Vector3[lightCount];

        for (int i = 0; i < lightCount; i++)
        {
            timeOffsets[i] = Random.Range(0f, 1f); // Assign random phase shift
            rotationAxes[i] = Random.onUnitSphere; // Random rotation axis
        }
    }

    void Update()
    {
        for (int i = 0; i < lights.Count; i++)
        {
            if (lights[i] != null)
            {
                // Flickering effect
                float time = (Time.time * speed * multiplier) + timeOffsets[i];
                float intensity = Mathf.Lerp(minIntensity, maxIntensity, Mathf.PingPong(time, 1));
                lights[i].intensity = intensity;

                // Rotation effect
                lights[i].transform.Rotate(rotationAxes[i], rotationSpeed * Time.deltaTime);
            }
        }
    }
}
