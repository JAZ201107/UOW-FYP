import { StaticVar } from "./static.js"

const registerForm = document.getElementById('registerForm')
if (registerForm) {
    registerForm.addEventListener('submit', handleRegister)
}

const messagePara = document.getElementById('messagePara')

function setMessage(message) {
    messagePara.textContent = message
}

function handleRegister(event) {
    event.preventDefault()

    const registerEndpoint = `${StaticVar.BASE_URL}/api/registeruser/`
    let registerFormData = new FormData(registerForm)
    let objectData = Object.fromEntries(registerFormData)
    
    // Check if password1 is the same as password2
    if (objectData.password1 !== objectData.password2) {
        setMessage("Passwords do not match")
        return
    }
    else
        objectData.password = objectData.password1
    
        
    let bodyStr = JSON.stringify(objectData)
    const options = {
        method : "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: bodyStr
    }

    fetch(registerEndpoint, options)
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
        let timerInterval
        Swal.fire({
        title: 'Account successfully created',
        icon: 'success',
        html: 'Redirecting back to login page in <b></b> seconds.',
        timer: 3000,
        timerProgressBar: true,
        didOpen: () => {
            Swal.showLoading()
            const b = Swal.getHtmlContainer().querySelector('b')
            timerInterval = setInterval(() => {
            b.textContent = (Swal.getTimerLeft() / 1000).toFixed(0)
            }, 1000)
        },
        willClose: () => {
            clearInterval(timerInterval)
        }
        }).then((result) => {
        if (result.dismiss === Swal.DismissReason.timer) {
            console.log('redirecting...')
            window.location.replace(`${StaticVar.BASE_URL}`)
        }
        })
    })
    .catch(err =>{
        registerForm.reset()
        setMessage(err.message);
    })
}