# Common Audio Video Server

[![GitHub Actions][github-image-ci]][github-url]
[![TypeScript Style Guide][gts-image]][gts-url]
[![Node v12.13.0][node-image]][node-url]

## Getting Started

### Prerequisites

To run this project in the development mode, you'll need to have a basic environment with NodeJS 13+ installed. To use the database, you'll need to have MongoDB installed and running on your machine at the default port (27017).

### Installing

**Cloning the Repository**

```
$ git clone https://github.com/devclub-iitd/CommonAudioVideoServer.git

$ cd CommonAudioVideoServer
```

**Installing dependencies**

```
$ npm install
```

**Starting The Server In Development Node**

```
$ npm run watch-debug
```

## Routes

The base URL is: http://localhost:5000/api/

### Test Route

- **This is the route that you can use to check if the API is running properly.**

> http://localhost:5000/api/

| ENDPOINT | Method | Params | URL Params | Success Response | Error Response
|--|--|--|--|--|--|
| / | `GET`  | - | - |**Code:** 200 - OK<br />**Content:** `{ message:  "Hooray! Welcome to Common Audio Server!",data: null }`  |  **Code:** 500 - INTERNAL SERVER ERROR <br />**Content:** `{ error:  <A Message with a description of the Error> }`|

### Track

- **Upload a Track**

> http://localhost:5000/api/upload

For this request, you'll need to send the .mp3 file and all the [Track](#track) data. If you don't know how to send a file using a http client tool, here's an example of how to do it with [Postman](https://www.getpostman.com/).

| ENDPOINT | Method | Params | URL Params | Success Response | Error Response
|--|--|--|--|--|--|
| /upload | `POST`  | - | - |**Code:** 200 - OK <br />**Content:** `{` <br /> track: [Track](#track)<br /> `}` |  **Code:** 500 - INTERNAL SERVER ERROR<br />**Content:** `{ error:  <A Message with a description of the Error> }`
<br />

## Built With

- [NodeJS](https://nodejs.org/en/) - Build the server
- [body-Parser](https://github.com/expressjs/body-parser#readme) - Node.js body parsing middleware
- [express](https://expressjs.com/) - Router of the Application
- [MongoDB](https://www.mongodb.com/) - Database
- [mongoose](https://mongoosejs.com/) - Object Modeling + DB Connector
- [nodemon](https://nodemon.io/) - Process Manager used in the development
- [dotenv](https://github.com/motdotla/dotenv) - Environment loader
- [multer](https://github.com/expressjs/multer) - File Upload
- [gridFS-Stream](https://github.com/aheckmann/gridfs-stream) - Store and stream data from Database
- [gts](https://github.com/google/gts) - TS Linter and code style
- [prettier](https://github.com/prettier/prettier) - Code formatter

## License

[MIT](LICENSE)

[github-image-ci]: https://github.com/devclub-iitd/CommonAudioVideoServer/workflows/Node.js%20CI/badge.svg
[github-url]: https://github.com/devclub-iitd/CommonAudioVideoServer/actions
[gts-image]: https://img.shields.io/badge/code%20style-google-blueviolet.svg
[gts-url]: https://github.com/google/gts
[node-image]: https://img.shields.io/badge/Node-v12.13.0-blue.svg
[node-url]: https://nodejs.org/en/blog/release/v12.13.0
