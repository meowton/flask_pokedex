// Pokemon sprite change
let shiny_sprite_url =
  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/';
let default_sprint_url =
  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/';
document.addEventListener('click', function (e) {
    if (e.target.id === 'button-shiny') {
      document.querySelector(`.${getPokeId(e)} .poke_sprite`).src =
        `${shiny_sprite_url}/${cutPokeId(e)}.png`;
    } else if (e.target.id === 'button-default') {
      document.querySelector(`.${getPokeId(e)} .poke_sprite`).src =
        `${default_sprint_url}/${cutPokeId(e)}.png`;
    }
  },
  false
);

function getPokeId(ev) {
  return ev.target.parentElement.className;
}

function cutPokeId(ev) {
  let poke_id = getPokeId(ev);
  return poke_id.slice(8);
}

function getTextFromInput(inputName) {
  return document.getElementById(inputName).value.trim().toLowerCase();
}

let search_poke = document.getElementById('name_search');
search_poke.addEventListener('keydown', function (e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    document.getElementById('search_button').click();
  }
});

// Bulma navbar script
document.addEventListener('DOMContentLoaded', () => {

  // Get all "navbar-burger" elements
  const $navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll('.navbar-burger'), 0);

  // Check if there are any navbar burgers
  if ($navbarBurgers.length > 0) {

    // Add a click event on each of them
    $navbarBurgers.forEach(el => {
      el.addEventListener('click', () => {

        // Get the target from the "data-target" attribute
        const target = el.dataset.target;
        const $target = document.getElementById(target);

        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        el.classList.toggle('is-active');
        $target.classList.toggle('is-active');

      });
    });
  }

});

