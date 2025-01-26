using UnityEngine;
using static UnityEngine.InputSystem.LowLevel.InputStateHistory;

public class DJ : MonoBehaviour
{
    public Animator animator;

    [Header("Record Components")]
    public GameObject recordPrefab;
    public Transform coverSocket;
    public GameObject recordDisc;
    public Transform discSocket;
    public Transform trackLocation;

    private GameObject instantiatedRecordCover;
    private RecordDisc recordScript;

    void Start()
    {
        if (recordDisc != null)
        {
            recordScript = recordDisc.GetComponent<RecordDisc>();
        }
    }

    public void PlayPickUpAnimation()
    {
        if (animator != null)
        {
            animator.SetTrigger("Pick up Vinyl");

            if (recordPrefab != null && coverSocket != null)
            {
                instantiatedRecordCover = Instantiate(recordPrefab, coverSocket.position, coverSocket.rotation);
                instantiatedRecordCover.transform.SetParent(coverSocket);
            }

            if (recordDisc != null && discSocket != null)
            {
                recordDisc.transform.SetParent(discSocket);
                recordDisc.transform.localPosition = Vector3.zero;
                recordDisc.transform.localRotation = Quaternion.identity;

                if (recordScript != null)
                {
                    recordScript.isSpinning = false;
                }
            }
        }
    }

    public void DropRecordToTrack()
    {
        if (recordDisc != null && trackLocation != null)
        {
            recordDisc.transform.SetParent(null);
            recordDisc.transform.position = trackLocation.position;
            recordDisc.transform.rotation = trackLocation.rotation;

            if (recordScript != null)
            {
                recordScript.isSpinning = true;
            }
        }
    }

    public void DestroyRecordCover()
    {
        if (instantiatedRecordCover != null)
        {
            Destroy(instantiatedRecordCover);
        }
    }
}
