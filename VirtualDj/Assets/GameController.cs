using UnityEngine;

public class GameController : MonoBehaviour
{
    public DJ djManager;

    void pickUpRecord()
    {
        djManager.PlayPickUpAnimation();
    }
}
