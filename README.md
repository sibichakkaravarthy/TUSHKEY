# TUSHKEY
TUSH-Key: Transferable User Secrets on Hardware Key

Passwordless authentication was first tested for seamless and secure merchant payments without the use of passwords or pins. It opened a whole new world of authentications giving up the former reliance on traditional passwords. It relied on the W3C Web Authentication (WebAuthn) and Client to Authenticator Protocol (CTAP) standards to use the public key cryptosystem to uniquely attest a user's device and then their identity. These standards comprise of the FIDO authentication standard. As the popularity of passwordless is increasing, more and more users and service providers are adopting to it. However, the concept of device attestation makes it device-specific for a user. It makes it difficult for a user to switch devices. FIDO Passkeys were aimed at solving the same, synchronizing the private cryptographic keys across multiple devices so that the user can perform passwordless authentication even from devices not explicitly enrolled with the service provider. However, passkeys have certain drawbacks including that it uses proprietary end to end encryption algorithms, all keys pass through proprietary cloud provider, and it is usually not very seamless when dealing with cross-platform key synchronization. To deal with the problems and drawbacks of FIDO Passkeys, the paper proposes a novel private key management system for passwordless authentication called Transferable User Secret on Hardware Key (TUSH-Key). TUSH-Key allows cross-platform synchronization of devices for seamless passwordless logins with FIDO2 specifications. 

Authors:
Aditya Mitra
Anisha Ghosh
Sibi Chakkaravarthy Sethuraman 
Rakesh Thoppean Babu
