const Moralis = require('moralis').default;

const express = require('express');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');

// to use our .env variables
require('dotenv').config();

const app = express();
const port = 4000;

app.use(express.json());
app.use(cookieParser());

// allow access to React app domain
app.use(
  cors({
    origin: 'http://localhost:3000',
    credentials: true,
  })
);

const config = {
  domain: process.env.APP_DOMAIN,
  statement: 'Please sign this message to confirm your identity.',
  uri: process.env.REACT_URL,
  timeout: 60,
};

// request message to be signed by client
app.post('/request-message', async (req, res) => {
    console.log("sdffewfcdcdwcdccd")
    // console.log(config)

  const { address, chain } = req.body;
  try {
    const message = await Moralis.Auth.requestMessage({
      address,
      chain,
      ...config,
    });
    // console.log(message)
    res.status(200).json(message);
  } catch (error) {
    res.status(400).json({ error: error.message });
    console.error(error);
  }
});




app.post('/verify', async (req, res) => {
  try {
    console.log(req.body)
    const { message, signature } = req.body;

    const { address, profileId } = (
      await Moralis.Auth.verify({
        message,
        signature,
      })
    ).raw;

    const user = { address, profileId, signature };

    // create JWT token
    const token = jwt.sign(user, process.env.AUTH_SECRET);

    // set JWT cookie
    res.cookie('jwt', token, {
      httpOnly: true,
    });

    res.status(200).json(user);
  } catch (error) {
    res.status(400).json({ error: error.message });
    console.error(error);
  }
});

app.get('/authenticate', async (req, res) => {
  const token = req.cookies.jwt;
  if (!token) return res.sendStatus(403); // if the user did not send a jwt token, they are unauthorized

  try {
    console.log("hello token")
    console.log(token)
    const data = jwt.verify(token, process.env.AUTH_SECRET);
    console.log("data")
    console.log(data)
    res.json(data);
  } catch {
    return res.sendStatus(403);
  }
});

app.get('/logout', async (req, res) => {
  try {
    res.clearCookie('jwt');
    return res.sendStatus(200);
  } catch {
    return res.sendStatus(403);
  }
});

const startServer = async () => {
  await Moralis.start({
    apiKey: process.env.MORALIS_API_KEY,
  });

  app.listen(port, () => {
    console.log(`Example app listening on port ${port}`);
  });
};

startServer();
