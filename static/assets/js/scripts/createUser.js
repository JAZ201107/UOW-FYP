import { StaticVar } from "./static.js"

const token = localStorage.getItem('token')
const createUserForm = document.getElementById('createUser')
if (createUserForm) {
    createUserForm.addEventListener('submit', handleRegister)
}

const messagePara = document.getElementById('message')

function setMessage(message) {
    messagePara.textContent = message
}

function handleRegister(event) {
    event.preventDefault()

    const createUserEndpoint = `${StaticVar.BASE_URL}/api/users/`
    let createUserData = new FormData(createUserForm)
    let objectData = Object.fromEntries(createUserData)
    let bodyStr = JSON.stringify(objectData)
    const options = {
        method : "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Token ${token}`
        },
        body: bodyStr
    }

    fetch(createUserEndpoint, options)
    .then(response=>{
        console.log(response)
        // Throw errors
        if (!response.ok) {
            return response.json()
            .then(errors => {
                let errArray1 = errors.email
                let errArray2 = errors.password
                if (errArray1 != null)
                    throw new Error(errArray1[0])
                
                if (errArray2 != null)
                    throw new Error(errArray2[0])
             })
        }
        return response.json()
    })
    .then(data=>{
        createUserForm.reset()
        Swal.fire({
        title: 'Account successfully created',
        icon: 'success',
        })
    })
    .catch(err =>{
        createUserForm.reset()
        setMessage(err.message);
    })
}