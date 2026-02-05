<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Squad Letterboxd Stats</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .custom-scroll::-webkit-scrollbar { width: 6px; }
        .custom-scroll::-webkit-scrollbar-track { background: #1f2937; }
        .custom-scroll::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 10px; }
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <header class="mb-12">
            <h1 class="text-5xl font-black text-green-400 italic uppercase tracking-tighter">Squad Stats</h1>
            <p class="text-gray-500 font-medium">Letterboxd Aggregate Intelligence</p>
        </header>
        
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div class="lg:col-span-4 space-y-6">
                <div class="bg-gray-800 p-6 rounded-3xl shadow-2xl border border-gray-700">
                    <h2 class="text-sm font-black uppercase tracking-widest mb-4 text-gray-400">1. The Crew</h2>
                    <div id="userInputsContainer" class="max-h-60 overflow-y-auto pr-2 custom-scroll flex flex-col gap-3 mb-6">
                        <div class="flex gap-2">
                            <input type="text" placeholder="Username" class="username-input bg-gray-900 p-4 rounded-2xl border border-gray-700 focus:outline-none focus:border-green-500 flex-1 text-sm font-bold">
                            <button onclick="addInput()" class="bg-gray-700 hover:bg-gray-600 px-5 rounded-2xl transition font-black text-xl">+</button>
                        </div>
                    </div>
                    
                    <h2 class="text-sm font-black uppercase tracking-widest mb-4 text-gray-400">2. Since Date</h2>
                    <input id="sinceDate" type="date" class="w-full bg-gray-900 p-4 rounded-2xl border border-gray-700 focus:outline-none mb-8 text-sm font-bold">
                    
                    <button onclick="fetchAllData()" id="fetchBtn" class="w-full bg-green-500 hover:bg-green-400 text-gray-900 py-5 rounded-2xl font-black uppercase tracking-widest transition-all transform hover:scale-[1.02] active:scale-95 shadow-xl shadow-green-500/20">
                        Generate Report
                    </button>
                </div>
                <div id="status" class="text-center text-xs font-black uppercase tracking-widest text-gray-600"></div>
            </div>

            <div id="dashboard" class="lg:col-span-8 space-y-8 hidden">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-gray-800 p-8 rounded-3xl border border-green-500/30">
                        <p class="text-green-500 text-xs font-black uppercase tracking-widest mb-2">Group MVP (Highest Avg)</p>
                        <div id="highestRated" class="text-2xl font-black text-white">--</div>
                    </div>
                    <div class="bg-gray-800 p-8 rounded-3xl border border-blue-500/30">
                        <p class="text-blue-400 text-xs font-black uppercase tracking-widest mb-2">Most Watched Film</p>
                        <div id="topMovie" class="text-2xl font-black text-white">--</div>
                    </div>
                </div>

                <div class="bg-gray-800 p-8 rounded-3xl border border-gray-700">
                    <h3 class="text-gray-500 text-xs font-black uppercase mb-6 tracking-widest">Genre Distribution</h3>
                    <div class="h-80 w-full">
                        <canvas id="genreChart"></canvas>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-gray-800 p-6 rounded-3xl">
                        <h3 class="text-green-500 text-xs font-black uppercase mb-4 tracking-widest">🏆 Top 5 Rated</h3>
                        <div id="top5Rated" class="space-y-3"></div>
                    </div>
                    <div class="bg-gray-800 p-6 rounded-3xl">
                        <h3 class="text-red-500 text-xs font-black uppercase mb-4 tracking-widest">📉 Bottom 5 Rated</h3>
                        <div id="bottom5Rated" class="space-y-3"></div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-gray-800 p-6 rounded-3xl">
                        <h3 class="text-purple-400 text-xs font-black uppercase mb-4 tracking-widest">🎬 Top Directors</h3>
                        <div id="topDirectorsList" class="space-y-2"></div>
                    </div>
                    <div class="bg-gray-800 p-6 rounded-3xl">
                        <h3 class="text-yellow-400 text-xs font-black uppercase mb-4 tracking-widest">👤 Top Actors</h3>
                        <div id="topActorsList" class="space-y-2"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let myChart = null;

        function addInput() {
            const container = document.getElementById('userInputsContainer');
            const div = document.createElement('div');
            div.className = "flex gap-2";
            div.innerHTML = `
                <input type="text" placeholder="Username" class="username-input bg-gray-900 p-4 rounded-2xl border border-gray-700 focus:outline-none focus:border-green-500 flex-1 text-sm font-bold">
                <button onclick="this.parentElement.remove()" class="bg-red-900/20 text-red-500 hover:bg-red-900/40 px-5 rounded-2xl transition">×</button>
            `;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        async function fetchAllData() {
            const inputs = document.querySelectorAll('.username-input');
            const usernames = Array.from(inputs).map(i => i.value.trim()).filter(v => v !== "");
            const date = document.getElementById('sinceDate').value;
            const btn = document.getElementById('fetchBtn');
            const status = document.getElementById('status');

            if (usernames.length === 0) return alert("Add at least one user.");

            btn.disabled = true;
            status.innerText = "Crunching squad data...";

            try {
                const results = await Promise.all(usernames.map(user => 
                    fetch(`/api/get-history?username=${user}&since=${date}`).then(res => res.json())
                ));

                const movieStats = {}; 
                const genreCounts = {};
                const directorCounts = {};
                const actorCounts = {};

                // Process every single entry
                results.flat().forEach(movie => {
                    const title = movie.title;
                    if (!title || title.toLowerCase() === 'unknown') return;

                    // Aggregate Movie Stats
                    if (!movieStats[title]) {
                        movieStats[title] = { title, watchCount: 0, ratings: [] };
                    }
                    movieStats[title].watchCount++;
                    if (movie.rating) movieStats[title].ratings.push(parseFloat(movie.rating));

                    // Aggregate Directors (Counting every entry/watch)
                    if (movie.director && movie.director !== "Unknown") {
                        directorCounts[movie.director] = (directorCounts[movie.director] || 0) + 1;
                    }

                    // Aggregate Actors & Genres
                    movie.genres.forEach(g => genreCounts[g] = (genreCounts[g] || 0) + 1);
                    movie.actors.forEach(a => actorCounts[a] = (actorCounts[a] || 0) + 1);
                });

                const statsArray = Object.values(movieStats).map(m => ({
                    ...m,
                    avgRating: m.ratings.length ? (m.ratings.reduce((a, b) => a + b, 0) / m.ratings.length) : null
                }));

                if (statsArray.length === 0) {
                    status.innerText = "No results found.";
                    return;
                }

                renderDashboard(statsArray, genreCounts, directorCounts, actorCounts);
                document.getElementById('dashboard').classList.remove('hidden');
                status.innerText = "Done.";
            } catch (err) {
                status.innerText = "Error fetching data.";
                console.error(err);
            } finally {
                btn.disabled = false;
            }
        }

        function renderDashboard(stats, genres, directors, actors) {
            const rated = stats.filter(s => s.avgRating !== null).sort((a, b) => b.avgRating - a.avgRating);
            const watched = [...stats].sort((a, b) => b.watchCount - a.watchCount);

            // Update Top Cards
            const topRated = rated[0];
            const mostWatched = watched[0];

            document.getElementById('highestRated').innerHTML = `
                ${topRated?.title || "N/A"} 
                <span class="text-green-500 block text-sm mt-1">${topRated ? topRated.avgRating.toFixed(1) + ' Avg Rating' : ''}</span>
            `;
            document.getElementById('topMovie').innerHTML = `
                ${mostWatched?.title || "N/A"} 
                <span class="text-blue-400 block text-sm mt-1">${mostWatched ? mostWatched.watchCount + ' Watches Total' : ''}</span>
            `;

            // Rankings
            renderList('top5Rated', rated.slice(0, 5), 'avgRating', '★');
            renderList('bottom5Rated', [...rated].reverse().slice(0, 5), 'avgRating', '★');
            
            // Cast/Crew (Counting Entries)
            const topDirs = Object.entries(directors).sort((a,b) => b[1] - a[1]).slice(0, 5);
            const topActs = Object.entries(actors).sort((a,b) => b[1] - a[1]).slice(0, 5);
            
            renderSimpleList('topDirectorsList', topDirs, 'entries');
            renderSimpleList('topActorsList', topActs, 'films');

            // Chart Rendering
            setTimeout(() => renderChart(genres), 200);
        }

        function renderList(id, data, key, unit) {
            const el = document.getElementById(id);
            el.innerHTML = data.map((item, i) => `
                <div class="flex justify-between items-center bg-gray-900/50 p-4 rounded-2xl border-l-4 ${id.includes('top5') ? 'border-green-500' : 'border-red-500'}">
                    <span class="text-sm font-black truncate pr-4">${item.title}</span>
                    <span class="text-sm font-mono font-black text-gray-400">
                        ${item[key].toFixed(1)}${unit}
                    </span>
                </div>
            `).join('') || '<p class="text-gray-600 text-xs italic">No data</p>';
        }

        function renderSimpleList(id, data, label) {
            const el = document.getElementById(id);
            el.innerHTML = data.map(([name, count]) => `
                <div class="flex justify-between items-center bg-gray-900/40 p-3 px-4 rounded-xl border border-gray-700">
                    <span class="text-sm font-bold">${name}</span>
                    <span class="text-xs font-black text-gray-500 uppercase tracking-tighter">${count} ${label}</span>
                </div>
            `).join('') || '<p class="text-gray-600 text-xs italic">No data</p>';
        }

        function renderChart(genreData) {
            const ctx = document.getElementById('genreChart').getContext('2d');
            if (myChart) myChart.destroy();

            const sorted = Object.entries(genreData).sort((a,b) => b[1] - a[1]).slice(0, 7);

            myChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: sorted.map(g => g[0]),
                    datasets: [{
                        data: sorted.map(g => g[1]),
                        backgroundColor: ['#4ade80', '#60a5fa', '#f87171', '#fbbf24', '#a78bfa', '#2dd4bf', '#f472b6'],
                        borderWidth: 0,
                        hoverOffset: 20
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '80%',
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: { color: '#9ca3af', font: { weight: 'bold', size: 12 }, padding: 20 }
                        }
                    }
                }
            });
        }
    </script>
</body>
</html>