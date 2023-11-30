# Proyecto de Simulación de Tráfico

Rodrigo Núñez Magallanes
y
Gabriel Rodríguez De Los Reyes

### Descripción del proyecto

El proyecto consiste en una simulación de coches en una pequeña ciudad con semáforos. La idea es simular un comportamiento en los coches, el cual consiste en llegar de un punto a otro, sin chocar con otros coches y respetando los semáforos. La parte visual de la simulación se realizará con Unity, y la parte lógica de la simulación, con Python, utilizando una librería llamada mesa.

# Visualización de simulación en Unity

Para visualizar la simulación en Unity, se debe correr el servidor de Python, y después correr la simulación en Unity. El servidor de Python se encuentra en la carpeta ```model```, y se corre con el archivo ```flask_server.py```. La simulación de Unity se encuentra en la carpeta ```TrafficVisualization```, que es el proyecto de Unity mismo.

## Instrucciones para correr la simulación

-  Correr el servidor de flask:

Una vez dentro del directorio ```model```, correr el siguiente comando:

```bash
$ python flask_server.py
```

- Una vez que el servidor esté corriendo, abrir el proyecto de Unity, y abrir la escena ```TrafficSimulation```. Una vez que la escena esté abierta, correr la simulación.

- Esta escena tiene el game object: ```AgentController``` que es responsable de hacer peticiones al servidor de flask para iniciar la simulación de mesa e irla actualizando. Esto se hace a través del script ```AgentController.cs```.

- También tiene el game object: ```CityMaker``` que genera la ciudad, y los agentes que la habitan. Esto se hace a través del script ```CityMaker.cs```. 

- Existe un script llamado ```CarManager.cs``` y otro ```SemaphorManager.cs```. El primero se encarga de mover los coches, y el segundo de cambiar los semáforos, en pocas palabras. El del auto inicializa sus llantas, las escala y posiciona, rota al auto, y lo mueve. El de los semáforos simplemente cambia el color de sus luces.

- En resumen, el ```AgentController``` es el encargado de hacer peticiones al servidor de flask e inicializar a todos los agentes, así como de asignar los valores de sus siguientes posiciones a los autos y destruirlos una vez que llegan a su destino, y el ```CityMaker``` es el encargado de generar la ciudad. Los scripts de los agentes se encargan de sus "funcionalidades".