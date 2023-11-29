/*
Funcionalidad de movimiento, rotacion, desplazamiento y escalado del coche.

Rodrigo Nunez, 2023-11-13
*/
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CarManager : MonoBehaviour
{
    bool initialized = false;
    // ------- LERP --------------------------------
    public Vector3 currentPos = new Vector3(0, 0, 0);
    public Vector3 targetPos;
    public Vector3 nextPos;
    float t;
    float moveTime = 1.0f;
    float elapsedTime = 0.0f;
    // --------------------------------------------
    // Wheel Game Objects
    public GameObject FrontLeftWheel;
    public GameObject FrontRightWheel;
    public GameObject RearLeftWheel;
    public GameObject RearRightWheel;
    float generalScale = 0.13f;
    float wheelScale = 0.35f;
    // All objects' meshes
    Mesh CarMesh;
    Mesh FrontLeftWheelMesh;
    Mesh FrontRightWheelMesh;
    Mesh RearLeftWheelMesh;
    Mesh RearRightWheelMesh;
    // Angle of rotation of the vehicle, which will be calculated
    int currentAngle;
    // Vertex arrays for the meshes and transformed vertices
    Vector3[] baseVertices;
    Vector3[] newVertices;
    Vector3[] baseFLWVertices;
    Vector3[] newFLWVertices;
    Vector3[] baseFRWVertices;
    Vector3[] newFRWVertices;
    Vector3[] baseRLWVertices;
    Vector3[] newRLWVertices;
    Vector3[] baseRRWVertices;
    Vector3[] newRRWVertices;
    // Start is called before the first frame update
    void Start()
    {
        //Instantiate Wheel Game Objects
        FrontLeftWheel = Instantiate(FrontLeftWheel);
        FrontRightWheel = Instantiate(FrontRightWheel);
        RearLeftWheel = Instantiate(RearLeftWheel);
        RearRightWheel = Instantiate(RearRightWheel);
        // Get the meshes
        CarMesh = GetComponentInChildren<MeshFilter>().mesh;
        FrontLeftWheelMesh = FrontLeftWheel.GetComponentInChildren<MeshFilter>().mesh;
        FrontRightWheelMesh = FrontRightWheel.GetComponentInChildren<MeshFilter>().mesh;
        RearLeftWheelMesh = RearLeftWheel.GetComponentInChildren<MeshFilter>().mesh;
        RearRightWheelMesh = RearRightWheel.GetComponentInChildren<MeshFilter>().mesh;
        // Assign mesh vertices to the vertex arrays
        baseVertices = CarMesh.vertices;
        baseFLWVertices = FrontLeftWheelMesh.vertices;
        baseFRWVertices = FrontRightWheelMesh.vertices;
        baseRLWVertices = RearLeftWheelMesh.vertices;
        baseRRWVertices = RearRightWheelMesh.vertices;
        // Allocate memory for the copy of the vertex list
        newVertices = new Vector3[baseVertices.Length];
        newFLWVertices = new Vector3[baseFLWVertices.Length];
        newFRWVertices = new Vector3[baseFRWVertices.Length];
        newRLWVertices = new Vector3[baseRLWVertices.Length];
        newRRWVertices = new Vector3[baseRRWVertices.Length];
        // Copy the coordinates
        for (int i = 0; i < baseVertices.Length; i++)
        {
            newVertices[i] = baseVertices[i];
        }
        for (int i = 0; i < baseFLWVertices.Length; i++)
        {
            newFLWVertices[i] = baseFLWVertices[i];
        }
        for (int i = 0; i < baseFRWVertices.Length; i++)
        {
            newFRWVertices[i] = baseFRWVertices[i];
        }
        for (int i = 0; i < baseRLWVertices.Length; i++)
        {
            newRLWVertices[i] = baseRLWVertices[i];
        }
        for (int i = 0; i < baseRRWVertices.Length; i++)
        {
            newRRWVertices[i] = baseRRWVertices[i];
        }
    }

    // Update is called once per frame
    void Update()
    {
        DoTransform();
    }

    void DoTransform()
    {
        // ------ LERP --------------------------------
        t = elapsedTime / moveTime;
        // t = t * t * (3.0f - 2.0f * t); suavisar movimiento
        Vector3 position = currentPos + (targetPos - currentPos) * t;
        Matrix4x4 move = OurTransform.Translate(position.x,
                                                      position.y,
                                                      position.z);
        elapsedTime += Time.deltaTime;
        if (elapsedTime >= moveTime)
        {
            currentPos = targetPos;
            targetPos = nextPos;
            elapsedTime = 0.0f;
        }
        // --------------------------------------------
        // Create the matrices
        // Y AXIS is ignored so that it can never go up
        Matrix4x4 translate = OurTransform.Translate(targetPos.x - currentPos.x, 0, targetPos.z - currentPos.z);
        Matrix4x4 rotate = OurTransform.Rotate(90 * Time.time, AXIS.X);
        // Calculate rotation angle given target and current position
        Vector3 target = new Vector3(targetPos.x - currentPos.x, 0f, targetPos.z - currentPos.z);
        Vector3 relative = transform.InverseTransformPoint(target);
        float calculatedAngle = Mathf.Atan2(relative.x, relative.z) * Mathf.Rad2Deg;
        if (currentPos == targetPos)
        {
            // If the car is not moving, it should not rotate, it should keep the same angle
        }
        else if (calculatedAngle == 0f)
        {
            currentAngle = 0;
        }
        else if (calculatedAngle > 0f)
        {
            currentAngle = (int)calculatedAngle;
        }
        else
        {
            currentAngle = (int)calculatedAngle + 360;
        }
        Matrix4x4 rotateObj = OurTransform.Rotate(-currentAngle, AXIS.Y);
        Matrix4x4 scaleWheel = OurTransform.Scale(wheelScale, wheelScale, wheelScale);
        Matrix4x4 scaleCar = OurTransform.Scale(generalScale, generalScale, generalScale);
        // ------------- CAR ----------------
        // Combine all the matrices into a single one
        Matrix4x4 composite = rotateObj * scaleCar;
        // If the car has received a second target position, it means it has to move with LERP
        if (!initialized)
        {
            composite = translate * composite;
            initialized = true;
        }
        else
        {
            composite = move * composite;
        }
        // Multiply each vertex in the mesh by the composite matrix
        for (int i = 0; i < newVertices.Length; i++)
        {
            var prev = baseVertices[i];
            Vector4 temp = new Vector4(prev.x, prev.y, prev.z, 1);
            newVertices[i] = composite * temp;
        }
        // Replace the vertices in the mesh
        CarMesh.vertices = newVertices;
        CarMesh.RecalculateNormals();
        CarMesh.RecalculateBounds();

        // ------------- WHEELS ----------------
        // -- Front Left Wheel --
        Matrix4x4 positionFLWheel = OurTransform.Translate(-0.95f, 0.4f, 1.5f);
        Matrix4x4 compositeFLWheel = composite * positionFLWheel * rotate * scaleWheel;
        for (int i = 0; i < newFLWVertices.Length; i++)
        {
            var prev = baseFLWVertices[i];
            Vector4 temp = new Vector4(prev.x, prev.y, prev.z, 1);
            newFLWVertices[i] = compositeFLWheel * temp;
        }
        FrontLeftWheelMesh.vertices = newFLWVertices;
        FrontLeftWheelMesh.RecalculateNormals();
        FrontLeftWheelMesh.RecalculateBounds();

        // -- Front Right Wheel --
        Matrix4x4 positionFRWheel = OurTransform.Translate(0.95f, 0.4f, 1.5f);
        Matrix4x4 compositeFRWheel = composite * positionFRWheel * rotate * scaleWheel;
        for (int i = 0; i < newFRWVertices.Length; i++)
        {
            var prev = baseFRWVertices[i];
            Vector4 temp = new Vector4(prev.x, prev.y, prev.z, 1);
            newFRWVertices[i] = compositeFRWheel * temp;
        }
        FrontRightWheelMesh.vertices = newFRWVertices;
        FrontRightWheelMesh.RecalculateNormals();
        FrontRightWheelMesh.RecalculateBounds();

        // -- Rear Left Wheel --
        Matrix4x4 positionRLWheel = OurTransform.Translate(-0.95f, 0.4f, -1.4f);
        Matrix4x4 compositeRLWheel = composite * positionRLWheel * rotate * scaleWheel;
        for (int i = 0; i < newRLWVertices.Length; i++)
        {
            var prev = baseRLWVertices[i];
            Vector4 temp = new Vector4(prev.x, prev.y, prev.z, 1);
            newRLWVertices[i] = compositeRLWheel * temp;
        }
        RearLeftWheelMesh.vertices = newRLWVertices;
        RearLeftWheelMesh.RecalculateNormals();
        RearLeftWheelMesh.RecalculateBounds();

        // -- Rear Right Wheel --
        Matrix4x4 positionRRWheel = OurTransform.Translate(0.95f, 0.4f, -1.4f);
        Matrix4x4 compositeRRWheel = composite * positionRRWheel * rotate * scaleWheel;
        for (int i = 0; i < newRRWVertices.Length; i++)
        {
            var prev = baseRRWVertices[i];
            Vector4 temp = new Vector4(prev.x, prev.y, prev.z, 1);
            newRRWVertices[i] = compositeRRWheel * temp;
        }
        RearRightWheelMesh.vertices = newRRWVertices;
        RearRightWheelMesh.RecalculateNormals();
        RearRightWheelMesh.RecalculateBounds();
    }
}
