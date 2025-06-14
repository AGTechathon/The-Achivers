function saveSignUpDetails() {
  // Prevent form submission
  event.preventDefault();

 // Get user input values
  const fullName = document.getElementById("fullName").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const confirmPassword = document.getElementById("confirmPassword").value.trim();
  const termsAccepted = document.getElementById("terms").checked;

 
  // Create a user object
  const user = {
      fullName,
      email,
      password, // Note: Passwords should not be stored in plain text in a real application
  };

  // Get existing users from localStorage or initialize an empty array
  let users = JSON.parse(localStorage.getItem("users")) || [];

  // Check if email already exists
  const emailExists = users.some((u) => u.email === email);
  if (emailExists) {
      alert("An account with this email already exists.");
      return;
  }

  // Add the new user to the array
  users.push(user);

  // Save the updated users array to localStorage
  localStorage.setItem("users", JSON.stringify(users));

  // Confirmation message and redirect
  alert("Sign-up successful!");
  window.location.href = "login.html";
}