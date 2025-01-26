using UnityEngine;

public class RecordDisc : MonoBehaviour
{
    public bool isSpinning = false;
    public float spinSpeed = 360f;

    void Update()
    {
        if (isSpinning)
        {
            transform.Rotate(Vector3.up, spinSpeed * Time.deltaTime, Space.Self);
        }
    }
}