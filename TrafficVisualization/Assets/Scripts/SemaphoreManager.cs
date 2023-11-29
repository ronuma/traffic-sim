using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SemaphoreManager : MonoBehaviour
{
    public bool isGreen = false;
    // Start is called before the first frame update
    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {
        if (isGreen)
        {
            GetComponentInChildren<Light>().color = Color.green;
        }
        else
        {
            GetComponentInChildren<Light>().color = Color.red;
        }
    }
}
