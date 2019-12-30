
## PLC set up
This example uses Twincat 3, but any PLC system with support for OPC UA is compatible. 
1. Install the TF6100 OPC UA function from [here](https://beckhoff.com/english.asp?download/tc3-download-tf6xxx.htm?id=1957281419487578).
2. Create a new project in Twincat 3.
3. Adding license: 
   * In the 'Solution Explorer' panel, select SYSTEM > Licence. 
   * Click the 'Manage Licenses' tab. Scroll down and tick the TF6100 license checkbox.
   * The license should appear under 'Order Information' tab.
4. Follow the instruction [here](https://infosys.beckhoff.com/english.php?content=../content/1033/tcopcuaserver/54043195607150603.html&id=6458066282452053983) to configure the OPC UA namespace.
5. Add the following variables:

    ```
    VAR
        {attribute 'OPC.UA.DA' := '1'}
        J1 : REAL;
        {attribute 'OPC.UA.DA' := '1'}
        J2 : REAL;
        {attribute 'OPC.UA.DA' := '1'}
        J3 : REAL;
        {attribute 'OPC.UA.DA' := '1'}
        Connect : BOOL := TRUE;
    END_VAR
    ```
6. Activate and start the project.

## Simulation setup
This example uses Visual Components 4.1 Premium. 
* Open the 'DobotProgram.vcmx' file and navigate to the 'Connection' tab in Visual Components. 
* Edit the address of the server under the 'Properties' panels if necessary. 
* Start the simulation. The variables should be updated in the Twincat portal

## Dobot client setup
### On Windows: 
* Download and install python 3.7 [here](https://www.python.org/downloads/)
* Install the OPC UA library: 
  
  ```
  pip install opcua
  ```

* Add the DobotDll/Windows/x64 or DobotDll/Windows/x86 to the User's 'PATH' environment variable. Instructions can be found [here](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/) 
* Start the client: 

    ```
    python livepolling-client.py
    ```
If connected the robot should move accordingly to the simulation. 

### On Linux: 

#### Install Anaconda: 
* Download the Anaconda setup script for Linux [here](https://www.anaconda.com/distribution/#linux)

* Run the downloaded script: 
  
  ```
  bash Anaconda-latest-Linux-x86_64.sh
  ``` 
* Follow the installation wizard. Remember to initialize conda when prompt. If you are unsure about any settings, accept the defaults. You can change them later. 
* Test your installation with: 
  ```
  conda list
  ```
#### Setup the python virtual environment:
* Navigate to the directory of this repo and execute: 

  ```
  conda env create -f environment.yml
  ```
* Verify that the new 'dobot' environment was installed correctly: 
  
  ```
  conda env list
  ```
* Activate the enviroment: 
  
  ```
  conda activate dobot
  ```
#### Run the Dobot client: 
In the 'livepolling-client.py' modified the server address according to the Twincat runtime address: 

```
client = Client("opc.tcp://laptop:4840/") # change server address here
```
Then start the client: 

```
python livepolling-client.py
```
If connected the robot should move accordingly to the simulation.