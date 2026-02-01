using Newtonsoft.Json;

record struct SensorData(int AcX, int AcY, int AcZ, int GyX, int GyY, int GyZ);
record struct TrainObject(SensorData[] sensorData, int gesture);

class Program{
    public static void Main(){
        const string FILENAME = "right.json";

        var json = File.ReadAllText("../../pc_driver/data/" + FILENAME);
        if(json == null) throw new ArgumentNullException("file empty");

        TrainObject[] tos = JsonConvert.DeserializeObject<TrainObject[]>(json) ??
            throw new Exception("deserialization failed");

        TrainObject[] croppedObjects = tos.Select(to =>
            new TrainObject(to.sensorData.Take(38).ToArray(), to.gesture)
        ).ToArray();

        var modifiedJson = JsonConvert.SerializeObject(croppedObjects, Formatting.Indented);
        File.WriteAllText("../../pc_driver/data/new_" + FILENAME, modifiedJson);
    }
}
