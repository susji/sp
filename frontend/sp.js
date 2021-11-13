function objtoarr(obj) {
    let result = [];
    for (let i = 0; i < Object.keys(obj).length; i++) {
	result.push(obj[i]);
    }
    return Uint8Array.from(result);
}

async function encryptMessage(plaintext) {
    let key = await window.crypto.subtle.generateKey(
	{
	    name: "AES-CBC",
	    length: 256,
	},
	true,
	["encrypt", "decrypt"]
    );

    const iv = await window.crypto.getRandomValues(new Uint8Array(16));
    const ciphertext = await window.crypto.subtle.encrypt(
	{
	    name: "AES-CBC",
	    iv: iv
	},
	key,
	new TextEncoder().encode(plaintext),
    );
    
    return {
	ciphertext: ciphertext,
	iv: iv,
	key: await window.crypto.subtle.exportKey("jwk", key),
    };
}

async function decryptMessage(ciphertext, key, iv) {
    const keydec = await window.crypto.subtle.importKey(
	"jwk",
	key,
	"AES-CBC",
	true,
	["encrypt", "decrypt"]);

    return await window.crypto.subtle.decrypt(
	{
	    name: "AES-CBC",
	    iv: iv,
	},
	keydec,
	ciphertext,
    );
}

export { objtoarr, encryptMessage, decryptMessage };
