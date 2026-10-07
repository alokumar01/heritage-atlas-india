const menuButton = document.getElementById("mobile-menu-button");
const mobileMenu = document.getElementById("mobile-menu");

if (menuButton && mobileMenu) {

    menuButton.addEventListener("click", () => {
        mobileMenu.classList.toggle("hidden");
    });

}
