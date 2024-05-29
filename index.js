const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const multer = require('multer');
const cors = require('cors');
const path = require("path");
const fs = require('fs');

// Connect to MongoDB using Mongoose
mongoose.connect('mongodb://localhost:27017/face_recognition_db', {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('Error connecting to MongoDB:', err));

// Define Mongoose schema and model for known faces
const knownFaceSchema = new mongoose.Schema({
    name:{
        type:String,
        required:true},
    image:{
        data:Buffer,
        contentType:String
     }
});
const KnownFace = mongoose.model('KnownFace', knownFaceSchema);

// Initialize Express
const app = express();
const PORT = process.env.PORT || 5000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());
app.use(cors());

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
      cb(null, `${__dirname}/uploads`);
    },
    filename: function (req, file, cb) {
    cb(null, file.fieldname + '-' + Date.now());
    }
  })

  const upload = multer({ storage: storage,
    fileFilter: (req, file, cb) => {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    
        if (!allowedTypes.includes(file.mimetype)) {
          const error = new Error('Invalid file type');
          error.code = 'INVALID_FILE_TYPE';
          return cb(error, false);
        }
    
        cb(null, true);
      }
  });


// Route to add a known face to the database
app.post('/known-faces', upload.single('image'), async (req, res) => {
    const data = {
        name : req.body.name,
        image : {
            data: fs.readFileSync(path.join(__dirname + '/uploads/' + req.file.filename)),
            contentType: req.file.mimetype,
        }
    }
      try{
        const result = await KnownFace.create(data);
        fs.unlinkSync(path.join(__dirname + '/uploads/' + req.file.filename));
        return res.status(200).json(result); 
       
    }catch(err) {
        console.log(err.message);
    }
});

// Route to retrieve all known faces from the database
app.get('/known-faces', async (req, res) => {
    try {
        const knownFaces = await KnownFace.find({});
        const faces = knownFaces.map(face => ({
            name: face.name,
            data: face.image.data.toString('base64'),
            contentType: face.image.contentType,
        }));

        return res.status(200).json(faces);
    } catch (error) {
        console.error('Error retrieving known faces:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

// Route to retrieve a specific face image from the database


// Start server
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
