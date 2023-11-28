// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro for the base, Rodrigo Nunez for the cars. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public string id;
    public float x, y, z;

    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]

public class AgentsData
{
    /*
    The AgentsData class is used to store the data of all the agents.

    Attributes:
        positions (list): A list of AgentData objects.
    */
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

public class AgentController : MonoBehaviour
{
    /*
    The AgentController class is used to control the agents in the simulation.

    Attributes:
        serverUrl (string): The url of the server.
        getAgentsEndpoint (string): The endpoint to get the agents data.
        getObstaclesEndpoint (string): The endpoint to get the obstacles data.
        beginSimulationEndpoint (string): The endpoint to begin the simulation.
        updateEndpoint (string): The endpoint to update the simulation.
        agentsData (AgentsData): The data of the agents that is received from the server.
        prevAgentsData (AgentsData): The data of the agents in the previous frame.
        agents (Dictionary<string, GameObject>): A dictionary of the agents.
        updated (bool): A boolean to know if the simulation has been updated.
        agentPrefab (GameObject): The prefab of the agents.
        timeToUpdate (float): The time to update the simulation.
        timer (float): The timer to update the simulation.
        dt (float): The delta time.
    */
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string beginSimulationEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData;
    AgentsData prevAgentsData;
    Dictionary<string, GameObject> agents;
    bool updated = false;
    public GameObject agentPrefab;
    public float timeToUpdate = 1.0f;
    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();
        prevAgentsData = new AgentsData();
        agents = new Dictionary<string, GameObject>();
        timer = timeToUpdate;
        // Launches a couroutine to begin the simulation in the server.
        StartCoroutine(BeginSimulation());
    }

    private void Update()
    {
        if (timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }
        if (updated)
        {
            timer -= Time.deltaTime;
        }
    }

    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            StartCoroutine(GetAgentsData());
        }
    }

    IEnumerator BeginSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + beginSimulationEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Getting Agents positions");
            // Once the model has been initialized it launches a coroutine to get the agents data.
            StartCoroutine(GetAgentsData());
        }
    }

    IEnumerator GetAgentsData()
    {
        // The GetAgentsData method is used to get the agents data from the server.
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            foreach (AgentData agent in agentsData.positions)
            {
                // If agent is not in the dictionary, add it and initialize it
                if (!agents.ContainsKey(agent.id))
                {
                    Vector3 origin = new Vector3(0, 0, 0);
                    Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
                    agents[agent.id] = Instantiate(agentPrefab, origin, Quaternion.identity);
                    agents[agent.id].GetComponent<CarManager>().currentPos = newAgentPosition;
                    agents[agent.id].GetComponent<CarManager>().targetPos = newAgentPosition;
                }
                else
                {
                    // If agent is in the dictionary, update its position
                    Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
                    // Here we don't need to update the currentPos because it is updated in the CarManager script
                    agents[agent.id].GetComponent<CarManager>().targetPos = newAgentPosition;
                }
            }
            // If agent is not in the new agents data, destroy it
            foreach (AgentData prevAgent in prevAgentsData.positions)
            {
                if (!agentsData.positions.Exists(agent => agent.id == prevAgent.id))
                {
                    Destroy(agents[prevAgent.id]);
                    Destroy(agents[prevAgent.id].GetComponent<CarManager>().FrontLeftWheel);
                    Destroy(agents[prevAgent.id].GetComponent<CarManager>().FrontRightWheel);
                    Destroy(agents[prevAgent.id].GetComponent<CarManager>().RearLeftWheel);
                    Destroy(agents[prevAgent.id].GetComponent<CarManager>().RearRightWheel);
                    agents.Remove(prevAgent.id);
                }
            }
            prevAgentsData = agentsData;
            updated = true;
        }
    }
}
