function StringToArray(str) {
    let result = [];
    for (let i = 0; i < str.length; i++) {
	result.push(str.charCodeAt(i));
    }
    return result;
}

function ObjectToArray(obj) {
    let result = [];
    for (let i = 0; i < Object.keys(obj).length; i++) {
	result.push(obj[i]);
    }
    return result;
}

async function generateKey() {
    return await window.crypto.subtle.generateKey(
	{
	    name: "AES-GCM",
	    length: 128,
	},
	true,
	["encrypt", "decrypt"]
    );
}

async function encryptMessage(plaintext) {
    const key = await generateKey();
    const iv = await window.crypto.getRandomValues(new Uint8Array(12));
    const ciphertext = await window.crypto.subtle.encrypt(
	{
	    name: "AES-GCM",
	    iv: iv
	},
	key,
	new TextEncoder().encode(plaintext),
    );

    console.log("iv: ", iv.length, iv);
    return {
	ciphertext: ciphertext,
	iv: iv,
	key: await window.crypto.subtle.exportKey("jwk", key),
    };
}

async function decryptMessage(ciphertext, key, iv) {
    console.log("key: ", key);
    const keydec = await window.crypto.subtle.importKey(
	"jwk",
	key,
	"AES-GCM",
	true,
	["encrypt", "decrypt"]);

    return await window.crypto.subtle.decrypt(
	{
	    name: "AES-GCM",
	    iv: iv,
	},
	keydec,
	ciphertext,
    );
}

export { StringToArray, ObjectToArray, encryptMessage, decryptMessage, generateKey };
