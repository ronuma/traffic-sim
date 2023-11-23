/*
Functions to work with transformation matrices in 3D

Gilberto Echeverria
2022-11-03
*/
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// Enumeration to define the axis
public enum AXIS { X, Y, Z };
// Values:        0  1  2

public class OurTransform : MonoBehaviour
{
    public static Matrix4x4 Translate(float tx, float ty, float tz)
    {
        Matrix4x4 matrix = Matrix4x4.identity;
        matrix[0, 3] = tx;
        matrix[1, 3] = ty;
        matrix[2, 3] = tz;
        return matrix;
    }

    public static Matrix4x4 Scale(float sx, float sy, float sz)
    {
        Matrix4x4 matrix = Matrix4x4.identity;
        matrix[0, 0] = sx;
        matrix[1, 1] = sy;
        matrix[2, 2] = sz;
        return matrix;
    }

    public static Matrix4x4 Rotate(float angle, AXIS axis)
    {
        float rads = angle * Mathf.Deg2Rad;
        float cosTheta = Mathf.Cos(rads);
        float sinTheta = Mathf.Sin(rads);

        Matrix4x4 matrix = Matrix4x4.identity;
        if (axis == AXIS.X)
        {
            matrix[1, 1] = cosTheta;
            matrix[1, 2] = -sinTheta;
            matrix[2, 1] = sinTheta;
            matrix[2, 2] = cosTheta;
        }
        else if (axis == AXIS.Y)
        {
            matrix[0, 0] = cosTheta;
            matrix[0, 2] = -sinTheta;
            matrix[2, 0] = sinTheta;
            matrix[2, 2] = cosTheta;
        }
        else if (axis == AXIS.Z)
        {
            matrix[0, 0] = cosTheta;
            matrix[0, 1] = -sinTheta;
            matrix[1, 0] = sinTheta;
            matrix[1, 1] = cosTheta;

        }
        return matrix;
    }
}