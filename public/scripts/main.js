
const api = "fcf8f7da9ef68f57fcd50b6179f9f8ca";

// GLOBALS:

let usersShow = []; // list of ids that depict which movies are show

// Sorting IDS
// arguments: 
//      1. list of users (if empty, everyone): FILTER
//		2. bool reverse

// takes ratings.json
// four type:
// 	server - server rating
//  imdb - imdb rating
//  alpha - 
// 	most - 
//  default - when added
// --- data: data["movies"]
function sortMovies(data)
{
	let out = {}
	let type = document.querySelector('input[name="sortOption"]:checked').value;
	if (type == "default")
	{
		out = data;
	}
	else if (type == "server")
	{
		let sortable = [];
		for (var movie in data) {
			sortable.push([movie, Number(data[movie]["avg"]), data[movie]]);
		}

		sortable.sort((a, b) => {
			return b[1] - a[1];
		});
		sortable.forEach(item => {
			out[item[0]] = item[2];
		});
	}
	else if (type == "alpha")
	{
		out = Object.keys(data)
			.sort()
			.reduce((acc, key) => { 
				acc[key] = data[key];
				return acc;
			}, {});
	}
	else if (type == "most")
	{
		let sortable = [];
		for (var movie in data) {
			sortable.push([movie, Object.keys(data[movie]["users"]).length, data[movie]]);
		}
		sortable.sort((a, b) => {
			return b[1] - a[1];
		});
		sortable.forEach(item => {
			out[item[0]] = item[2];
		});
	}

	if (document.querySelector("#reverseCheck").checked) {
		let temp = {};
		Object.keys(out).reverse().forEach((movie) => {
			temp[movie] = data[movie];
		});
		return temp;
	}
	return out;
}


document.querySelector("#selectNone").onchange = () => 
{
	let contain = document.querySelector("#navNamesContainer");
	for (let i = 0; i < contain.children.length; i++)
	{	
		contain.children[i].children[0].checked = false; // !important
	}
	usersShow = checkNone();	
}
document.querySelector("#selectAll").onchange = () =>
{
	let contain = document.querySelector("#navNamesContainer");
	for (let i = 0; i < contain.children.length; i++)
	{	
		contain.children[i].children[0].checked = true; // !important
	}
	usersShow = [];	
};

document.querySelector("#navSave").onclick = () =>
{
	loadMovies();
};

function checkNone()
{
	let copyUsersShow = usersShow;
	fetch("./users.json")
		.then(response => { return response.json(); })
		.then(users => {
			for (let user in users)
			{
				copyUsersShow.push(user);
				usersShow = copyUsersShow;
			}	
		});
}

// takes data and only returns movies that have the ids in usersShow
function filter(data) {
	// if (usersShow.length == 0) return [];
	let out = {};
	for (let movie in data) {
		if (usersShow.length == 0) out[movie] = data[movie]; // no filter
		else
		{
			let add = false;
			for (let user in data[movie]["users"])
			{
				if (!usersShow.includes(user))
				{
					add = true;
					break;
				}
			}
			if (add) out[movie] = data[movie];
		}
	}
	return out;
}


function sortRatings(movieUsers) {
	// { id: "rating"}
	// func (id) -> number(movieUsers["users"][id])

	let sortable = [];
	for (var id in movieUsers) {
		sortable.push([id, Number(movieUsers[id])]);
	}

	sortable.sort((a, b) => {
		return b[1] - a[1];
	});


	let out = {};
	sortable.forEach(item => {
		out[item[0]] = item[1];
	});
	return out;
}

function loadMovies() {
	// delete old movies

	const oldMovies = document.querySelector(".movies");
	oldMovies.remove();

	
	const newMovies = htmlToElement(
		`<div class="movies" class="container page-container">
			<div id="row0" class="row">
			</div>
  		</div>`);
	document.querySelector("#movieContainer").appendChild(newMovies);

	// repopulate

	fetch("./ratings.json")
		.then(response => { return response.json(); })
		.then(data => {
			fetch("./users.json")
				.then(response => { return response.json(); })
				.then(users => {
					let perRow = 6;
					let currentCol = 0;
					let rows = 0;
					// Populate Movies
					for (let name in sortMovies(filter(data["movies"]), "most")) {
						let listOfRatings = sortRatings(data["movies"][name]["users"]);
						const url = `https://api.themoviedb.org/3/movie/${data["movies"][name]["id"]}?api_key=fcf8f7da9ef68f57fcd50b6179f9f8ca`
						fetch(url)
							.then(response => { return response.json(); })
							.then(movie => {
								let listScores = "";
								for (let id in listOfRatings) {
									// console.log(users[id]["nameIRL"], movie["title"]);
									listScores += `<li>${users[id]["nameIRL"]}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${data["movies"][name]["users"][id]}</li>`
								}
								const card = htmlToElement(`
							<div class="col-xl-2 col-lg-4 col-md-5 col-sm-6">
								<div class="card-movie card" style="width: 18rem;">
									<div class="card-inner">
										<div class="card-front">
											<img class="card-img-top" src="https://image.tmdb.org/t/p/w500/${movie["poster_path"]}" height="432" alt="Card image cap">
										</div>
										<div class="card-back">
											<img class="movie-poster-back card-img-top" src="https://www.themoviedb.org/t/p/w1920_and_h800_multi_faces/${movie["backdrop_path"]}" alt="Card image cap">
											<div class="movie-title movie-ratings-header card-header">${movie["title"]}</div>
												<div class="movie-ratings card-body">
													<h5 class="card-title" style="text-align: center;"> - Ratings -</h5>
														<ul class="card-text">
															${listScores}
														</ul>
												</div>
												<div class="movie-footer card-footer">
													iMDB Rating: ${movie["vote_average"].toFixed(1)} <br>
													Server Rating: ${data["movies"][name]["avg"].toFixed(1)}
												</div>
											</div>
											
										</div>
										
									</div>
								</div>
							</div>`);
								document.querySelector(`#row${rows}`).appendChild(card);
								currentCol += 1;
								if (currentCol == perRow) {
									rows += 1;
									const newRow = htmlToElement(`<div id="row${rows}" class="row"></div>`);
									document.querySelector(".movies").appendChild(newRow);
									currentCol = 0;
								}
							})
					}
				});
		});
}


window.onload = function () {
	// loop through all of our moviesv --
	// pull information from movie api -- 
	// then insert into card
	fetch("./ratings.json")
		.then(response => { return response.json(); })
		.then(data => {
			fetch("./users.json")
				.then(response => { return response.json(); })
				.then(users => {
					let perRow = 6;
					let currentCol = 0;
					let rows = 0;
					//Navbar Options
					for (let user in users) {
						const checkbox = htmlToElement(`
						<div class="navCheckboxes form-check">
						<input class="form-check-input" type="checkbox" id="${users[user]["nameIRL"]}>
						<label class="form-check-label" for="${users[user]["nameIRL"]}">
							${users[user]["nameIRL"]}
						</label>
						</div>`);
						checkbox.children[0].checked = true;
						checkbox.children[0].onclick = () => {
							if (usersShow.includes(user)) {
								usersShow.splice(usersShow.indexOf(user), 1);
							} else {
								usersShow.push(user);
							}
						}
						document.querySelector("#navNamesContainer").appendChild(checkbox);
					}
				}
				)
		}
		);
	loadMovies();
};

function htmlToElement(html) {
	var template = document.createElement('template');
	html = html.trim(); // Never return a text node of whitespace as the result
	template.innerHTML = html;
	return template.content.firstChild;
}