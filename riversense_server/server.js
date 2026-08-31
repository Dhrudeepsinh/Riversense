// // const express = require("express");
// // const mongoose = require("mongoose");
// // const cors = require("cors");

// // const app = express();
// // app.use(express.json());
// // app.use(cors());

// // // MongoDB connection
// // mongoose.connect(process.env.MONGO_URI)
// // .then(() => console.log("MongoDB Connected"))
// // .catch(err => console.log(err));

// // // Schema
// // const TurbiditySchema = new mongoose.Schema({
// //   turbidity_value: Number,
// //   turbidity_status: Number,
// //   time: { type: Date, default: Date.now },
// // });

// // // Model (collection: waters)
// // const Turbidity = mongoose.model("Turbidity", TurbiditySchema, "waters");

// // // API
// // app.post("/data", async (req, res) => {
// //   try {
// //     const newData = new Turbidity({
// //       turbidity_value: req.body.turbidity_value,
// //       turbidity_status: req.body.turbidity_status,
// //     });

// //     await newData.save();
// //     res.send("Data Saved");
// //   } catch (err) {
// //     console.log(err);
// //     res.status(500).send(err);
// //   }
// // });

// // app.listen(3000, () => {
// //   console.log("Server running on port 3000");
// // });

// const express = require("express");
// const mongoose = require("mongoose");
// const cors = require("cors");

// const { SerialPort } = require("serialport");
// const { ReadlineParser } = require("@serialport/parser-readline");

// const app = express();
// app.use(express.json());
// app.use(cors());

// // ✅ MongoDB connection
// mongoose.connect(process.env.MONGO_URI)
// .then(() => console.log("MongoDB Connected"))
// .catch(err => console.log(err));

// // ✅ Combined Schema (ALL sensors)
// const SensorSchema = new mongoose.Schema({
//   turbidity_value: Number,
//   turbidity_status: Number,
//   pH: Number,
//   water_level: Number,
//   source: String, // "nodemcu" or "arduino"
//   time: { type: Date, default: Date.now },
// });

// // Collection: waters
// const Sensor = mongoose.model("Sensor", SensorSchema, "waters");


// // ================= NODEMCU API =================
// app.post("/data", async (req, res) => {
//   try {
//     const newData = new Sensor({
//       turbidity_value: req.body.turbidity_value,
//       turbidity_status: req.body.turbidity_status,
//       source: "nodemcu"
//     });

//     await newData.save();
//     console.log("NodeMCU Data:", req.body);

//     res.send("NodeMCU Data Saved");
//   } catch (err) {
//     console.log(err);
//     res.status(500).send(err);
//   }
// });


// // ================= ARDUINO SERIAL =================

// // ⚠️ Change COM port
// const port = new SerialPort({
//   path: "COM4",
//   baudRate: 9600
// });

// const parser = port.pipe(new ReadlineParser({ delimiter: "\n" }));

// parser.on("data", async (data) => {
//   try {
//     console.log("Arduino Raw:", data);

//     const json = JSON.parse(data);

//     const newData = new Sensor({
//       pH: json.pH,
//       water_level: json.water_level,
//       source: "arduino"
//     });

//     await newData.save();
//     console.log("Arduino Data Saved:", json);

//   } catch (err) {
//     console.log("Serial Error:", err.message);
//   }
// });


// // ================= SERVER =================
// app.listen(3000, () => {
//   console.log("Server running on port 3000");
// });

//--DUMMY----------------------------------
// const mongoose = require("mongoose");
// const { SerialPort } = require("serialport");
// const { ReadlineParser } = require("@serialport/parser-readline");

// mongoose.connect(process.env.MONGO_URI)
// .then(() => console.log("MongoDB Connected"));

// const SensorSchema = new mongoose.Schema({
//   turbidity_value: Number,
//   turbidity_status: Number,
//   pH: Number,
//   water_level: Number,
//   source: String,
//   time: { type: Date, default: Date.now },
// });

// const Sensor = mongoose.model("Sensor", SensorSchema, "waters");

// async function connectArduino() {
//   const ports = await SerialPort.list();

//   for (let p of ports) {
//     if (p.manufacturer && (p.manufacturer.includes("Arduino") || p.manufacturer.includes("CH340"))) {

//       const port = new SerialPort({
//         path: p.path,
//         baudRate: 9600,
//       });

//       const parser = port.pipe(new ReadlineParser({ delimiter: "\n" }));

//       parser.on("data", async (data) => {
//         try {
//           const json = JSON.parse(data);

//           await Sensor.create({
//             pH: json.pH,
//             water_level: json.water_level,
//             source: "arduino"
//           });

//           console.log("Saved:", json);

//         } catch (err) {
//           console.log("Parse Error:", err.message);
//         }
//       });

//       console.log("Connected to", p.path);
//       return;
//     }
//   }
// }

// connectArduino();
//-----------------------------------------
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const { SerialPort } = require("serialport");
const { ReadlineParser } = require("@serialport/parser-readline");

const app = express();
app.use(express.json());
app.use(cors());

// ================= MONGODB =================
mongoose.connect(process.env.MONGO_URI)
.then(() => console.log("MongoDB Connected"))
.catch(err => console.log(err));

// ================= SCHEMA =================
const SensorSchema = new mongoose.Schema({
  turbidity_value: Number,
  turbidity_status: Number,
  pH: Number,
  water_level: Number,
  source: String,
  time: { type: Date, default: Date.now },
});

const Sensor = mongoose.model("Sensor", SensorSchema, "waters");

// ================= NODEMCU API =================
app.post("/data", async (req, res) => {
  try {
    const newData = new Sensor({
      turbidity_value: req.body.turbidity_value,
      turbidity_status: req.body.turbidity_status,
      source: "nodemcu"
    });

    await newData.save();
    console.log("NodeMCU Data:", req.body);

    res.send("NodeMCU Data Saved");
  } catch (err) {
    console.log(err);
    res.status(500).send(err);
  }
});

// ================= AUTO SERIAL CONNECT =================
async function connectArduino() {
  try {
    const ports = await SerialPort.list();

    console.log("Available Ports:");
    ports.forEach(p => console.log(p.path, p.manufacturer));

    for (let p of ports) {
      try {
        console.log("Trying:", p.path);

        const port = new SerialPort({
          path: p.path,
          baudRate: 9600,
          autoOpen: false
        });

        port.open(err => {
          if (err) {
            console.log(`❌ Busy/Failed: ${p.path}`);
            return;
          }

          console.log(`✅ Connected to ${p.path}`);

          const parser = port.pipe(new ReadlineParser({ delimiter: "\n" }));

          parser.on("data", async (data) => {
            try {
              console.log("Arduino Raw:", data);

              const json = JSON.parse(data);

              const newData = new Sensor({
                pH: json.pH,
                water_level: json.water_level,
                source: "arduino"
              });

              await newData.save();
              console.log("✅ Arduino Data Saved:", json);

            } catch (err) {
              console.log("❌ Parse Error:", err.message);
            }
          });

        });

        return; // stop after first success

      } catch (err) {
        console.log("Error with port:", p.path);
      }
    }

    console.log("❌ No working port found");

  } catch (err) {
    console.log("Serial Error:", err);
  }
}

connectArduino();

// ================= SERVER =================
app.listen(3000, () => {
  console.log("Server running on port 3000");
});

//================Weather=====================
app.get("/api/weather", async (req, res) => {
  try {
    const response = await fetch(
      "https://api.open-meteo.com/v1/forecast?latitude=23.0225&longitude=72.5714&current_weather=true"
    );

    const data = await response.json();

    res.json(data.current_weather); // 👈 send only needed data
  } catch (error) {
    console.error("Weather API error:", error);
    res.status(500).json({ error: "Failed to fetch weather" });
  }
});


