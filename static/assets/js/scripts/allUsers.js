import { StaticVar } from "./static.js"

const token = localStorage.getItem('token')
const userTable = document.getElementById('usertbl')
const searchBar = document.getElementById('search')

// Debounce function to delay search request firing
function debounce(func, timeout = 300){
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
  }

searchBar.addEventListener("keyup", debounce(function(e) {
    const searchValue = e.target.value
    const searchUsersEndpoint = `${StaticVar.BASE_URL}/api/users/?` +
                                new URLSearchParams({
                                    email: searchValue
                                })
    const options = {
        method : "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Token ${token}`
            }
        }
    
    fetch(searchUsersEndpoint, options)
    .then(response=>{
        if (response.ok){
            return response.json()
        }
    })
    .then(data=>{
        userTable.innerHTML = ""
        if (userTable) {
            for (let i = 0; i < data.length; i++)
                addRow(data[i])
        } 
    })
}))

document.addEventListener("DOMContentLoaded", function(event) {
    const getUsersEndpoint = `${StaticVar.BASE_URL}/api/users`
    const options = {
        method : "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Token ${token}`
            }
        }
    
    fetch(getUsersEndpoint, options)
    .then(response=>{
        if (response.ok){
            return response.json()
        }
    })
    .then(data=>{
        if (userTable) {
            for (let i = 0; i < data.length; i++)
                addRow(data[i])
        } 
    })
})

document.body.addEventListener("click", function(e) {
    let buttonClass = e.target.className
    let buttonId = e.target.id
    
     if (buttonClass === "changepwbtn") {
        let userEmail = e.target.parentElement.previousSibling.previousSibling.innerHTML
        const changePasswordEndpoint = `${StaticVar.BASE_URL}/api/users/${buttonId}/`
        
        Swal.fire({
            title: `Change password for ${userEmail}`,
            html:
            '<label>Enter new password</label>' +
            '<input id="password1" type="password" class="swal2-input">' +
            '<label>Confirm new password</label>' +
            '<input id="password2" type="password" class="swal2-input">',
            inputAttributes: {
              autocapitalize: 'off'
            },
            showCancelButton: true,
            confirmButtonText: 'Change Password',
            showLoaderOnConfirm: true,
            preConfirm: () => {
                let password = document.getElementById('password1').value
                let password2 = document.getElementById('password2').value
                const options = {
                    method : "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Token ${token}`
                    },
                    body: JSON.stringify({
                        "password": `${password}`,
                        "password2": `${password2}`
                      })
                }
              return fetch(changePasswordEndpoint, options)
                .then(response => {
                  if (!response.ok) {
                    return response.json()
                    .then(errors => {
                        let errArray1 = errors.password
                        let errArray2 = errors.password2
                        if (errArray1 != null)
                            throw new Error(errArray1[0])
                        
                        if (errArray2 != null)
                            throw new Error(errArray2[0])
                     })
                    
                  }
                  return response.json()
                })
                .catch(error => {
                  Swal.showValidationMessage(
                    error.message
                  )
                })
            },
            allowOutsideClick: () => !Swal.isLoading()
          }).then((result) => {
            if (result.isConfirmed) {
            Swal.fire({
                title: `${userEmail}'s password successfully changed`
            })
            }
          })
     }

     if (buttonClass === "deleteuserbtn") {
        let userEmail = e.target.parentElement.previousSibling.previousSibling.previousSibling.innerHTML
        let userRow = e.target.parentElement.parentElement
        Swal.fire({
            title: `Are you sure you want to delete user ${userEmail}`,
            text: 'This action cannot be reverted',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#FF0000',
            confirmButtonText: 'Delete',
        })
        .then(result => {
            if (result.isConfirmed) {
                const deleteUserEndpoint = `${StaticVar.BASE_URL}/api/users/${buttonId}/`
                const options = {
                    method : "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Token ${token}`
                    }
                }

                fetch (deleteUserEndpoint, options)
                .then(response=>{
                    if (response.ok) {
                        userRow.remove()
                    }
                })
            }
        })
     }
  })

function addRow(user) {
    var row = userTable.insertRow()
    var cell1 = row.insertCell(0)
    var cell2 = row.insertCell(1)
    var cell3 = row.insertCell(2)
    var cell4 = row.insertCell(3)

    cell1.innerHTML = user.email
    if (user.is_admin)
        cell2.innerHTML = 'Yes'
    else
        cell2.innerHTML = 'No'
    cell3.innerHTML = `<button id=${user.id} class="changepwbtn">Change Password</button>`
    cell4.innerHTML = `<button id=${user.id} class="deleteuserbtn">Delete User</button>`
}