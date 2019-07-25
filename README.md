# Black Metropolis Research Consortium (BMRC)
Mocks for stake holder approval for the Black Metropolis Research Consortium website.

## Quick Start
These mocks run on Gulp and offer auto-compiling and local browser refresh.
Site is running on a customized Sass Bulma framework. Read the [Bulma documentation](https://bulma.io/documentation/) for how the grid and class systems work. Variables for extra customization can be found in the [Custom Bulma Documentation](https://bulma.io/documentation/customize/variables/).

### Install the required npm items
`npm install`  - Installs required npm packages
`gulp` - Runs task manager; opens local host

### Local Host
Task manager auto runs `port3000` when the gulp command is initiated.
All changes are auto refreshed in your local host.

## Styles
Only edit the Sass files. Run the gulp task to compile changes and created the CSS files.

- variables.scss:  partial Sass file that controls all variables used in other style sheets.
- style.scss: Bulma customizations and local styles. Bulma base styles are imported through this file.
- carousel.scss: Animation and transitions for the hero slider on the homepage. Related files: active.js and plugins/plugins.js