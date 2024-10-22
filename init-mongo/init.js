const dbName = process.env.MONGODB_DB;
const username = process.env.MONGODB_USER;
const password = process.env.MONGODB_PASSWORD;

db = db.getSiblingDB(dbName);

db.createUser({
    user: username,
    pwd: password,
    roles: [{ role: 'readWrite', db: dbName }],
});
