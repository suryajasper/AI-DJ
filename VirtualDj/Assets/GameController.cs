using UnityEngine;

public class GameController : MonoBehaviour
{
    public Animator djAnimator;
    public DJ djManager;
    public LightManager lightManager;

    void pickUpRecord()
    {
        djManager.PlayPickUpAnimation();
    }

    void setSpeed(int speed)
    {
        speed = Mathf.Clamp(speed, 1, 5);
        djAnimator.SetInteger("Speed", speed);
        lightManager.speed = speed;
    }
}
