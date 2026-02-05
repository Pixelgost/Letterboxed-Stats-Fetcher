<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Squad Letterboxd Stats Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .custom-scroll::-webkit-scrollbar { width: 6px; }
        .custom-scroll::-webkit-scrollbar-track { background: #1f2937; }
        .custom-scroll::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 10px; }
        @keyframes pulse-slow { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .loading-pulse { animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen p-4 md:p-8 font-sans">
    <div class="max-w-6xl mx-auto">
        <h1 class="text-4xl font-black mb-8 text-green-400 italic uppercase tracking-tighter">Squad Stats Pro</h1>
        
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div class="lg:col-span-4 space-y-6">
                <div class="bg-gray-800 p-6 rounded-2xl shadow-2xl border border-gray-700">
                    <h2 class="text-lg font-bold mb-4 text-gray-300">1. Add Your Crew</h2>
                    <div id="userInputsContainer" class="max-h-60 overflow-y-auto pr-2 custom-scroll flex flex-col gap-3 mb-6">
                        <div class="flex gap-2">
                            <input type="text" placeholder="Username" class="username-input bg-gray-900 p-3 rounded-xl border border-gray-700 focus:outline-none focus:border-green-500 flex-1 text-sm">
                            <button onclick="addInput()" class="bg-gray-700 hover:bg-gray-600 px-4 rounded-xl transition font-bold">+</button>
                        </div>
                    </div>
                    
                    <h2 class="text-lg font-bold mb-4 text-gray-300">2. Timeframe</h2>
                    <input id="sinceDate" type="date" class="w-full bg-gray-900 p-3 rounded-xl border border-gray-700 focus:outline-none mb-6 text-sm">
                    
                    <button onclick="fetchAllData()" id="fetchBtn" class="w-full bg-green-600 hover:bg-green-500 py-4 rounded-xl font-black uppercase tracking-widest transition-all shadow-lg">
                        Generate Report
                    </button>
                </div>
                <div id="status" class="text-center text-sm text-gray-500 font-medium"></div>
            </div>

            <div id="dashboard" class="lg:col-span-8 space-y-6 hidden">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-gray-800 p-6 rounded-2xl border border-green-500/20 shadow-xl">
                        <p class="text-gray-500 text-xs font-black uppercase mb-1">Group MVP (Highest Avg)</p>
                        <div id="highestRated" class="text-xl font-bold text-white truncate">--</div>
                    </div>
                    <div class="bg-gray-800 p-6 rounded-2xl border border-blue-500/20 shadow-xl">
                        <p class="text-gray-500 text-xs font-black uppercase mb-1">Most Watched Film</p>
                        <div id="topMovie" class="text-xl font-bold text-white truncate">--</div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-gray-800 p-5 rounded-2xl border border-purple-500/20">
                        <h3 class="text-purple-400 text-[10px] font-black uppercase mb-4 tracking-widest">🎬 Top Directors</h3>
                        <div id="topDirectors" class="space-y-2"></div>
                    </div>
                    <div class="bg-gray-800 p-5 rounded-2xl border border-pink-500/20">
                        <h3 class="text-pink-400 text-[10px] font-black uppercase mb-4 tracking-widest">🎭 Top Genres</h3>
                        <div id="topGenres" class="space-y-2"></div>
                    </div>
                    <div class="bg-gray-800 p-5 rounded-2xl border border-orange-500/20">
                        <h3 class="text-orange-400 text-[10px] font-black uppercase mb-4 tracking-widest">🌟 Star Actors</h3>
                        <div id="topActors" class="space-y-2"></div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-gray-800 p-5 rounded-2xl">
                        <h3 class="text-green-500 text-[10px] font-black uppercase mb-4 tracking-widest">🏆 Top 5 Rated</h3>
                        <div id="top5Rated" class="space-y-2"></div>
                    </div>
                    <div class="bg-gray-800 p-5 rounded-2xl">
                        <h3 class="text-red-500 text-[10px] font-black uppercase mb-4 tracking-widest">📉 Bottom 5 Rated</h3>
                        <div id="bottom5Rated" class="space-y-2"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function addInput() {
            const container = document.getElementById('userInputsContainer');
            const div = document.createElement('div');
            div.className = "flex gap-2";
            div.innerHTML = `
                <input type="text" placeholder="Username" class="username-input bg-gray-900 p-3 rounded-xl border border-gray-700 focus:outline-none focus:border-green-500 flex-1 text-sm">
                <button onclick="this.parentElement.remove()" class="bg-red-900/30 text-red-400 hover:bg-red-900/50 px-4 rounded-xl transition">×</button>
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

            if (usernames.length === 0) return alert("Enter at least one username!");

            btn.disabled = true;
            btn.innerHTML = `<span class="loading-pulse">Scraping Metadata...</span>`;
            status.innerText = "This will take a moment as we fetch cast & crew for every movie...";

            try {
                const results = await Promise.all(usernames.map(user => 
                    fetch(`/api/get-history?username=${user}&since=${date}`).then(res => res.json())
                ));

                const watchCounts = {}; 
                const ratingsMap = {};
                const tallies = { directors: {}, genres: {}, actors: {} };

                results.forEach((userData) => {
                    userData.forEach(movie => {
                        const title = movie.title;
                        watchCounts[title] = (watchCounts[title] || 0) + 1;
                        
                        // Tallies for new stats
                        if(movie.director) tallies.directors[movie.director] = (tallies.directors[movie.director] || 0) + 1;
                        if(movie.genres) movie.genres.forEach(g => tallies.genres[g] = (tallies.genres[g] || 0) + 1);
                        if(movie.actors) movie.actors.forEach(a => tallies.actors[a] = (tallies.actors[a] || 0) + 1);

                        if(movie.rating) {
                            const val = parseFloat(movie.rating);
                            if(!ratingsMap[title]) ratingsMap[title] = [];
                            ratingsMap[title].push(val);
                        }
                    });
                });

                const stats = Object.keys(watchCounts).map(title => ({
                    title,
                    watchCount: watchCounts[title],
                    avgRating: ratingsMap[title] ? (ratingsMap[title].reduce((a,b)=>a+b,0)/ratingsMap[title].length) : null
                }));

                renderDashboard(stats, tallies);
                document.getElementById('dashboard').classList.remove('hidden');
                status.innerText = "Report Generated!";
            } catch (err) {
                status.innerText = "Error: Check backend connection.";
                console.error(err);
            } finally {
                btn.disabled = false;
                btn.innerText = "Generate Report";
            }
        }

        function renderDashboard(stats, tallies) {
            const rated = stats.filter(s => s.avgRating !== null).sort((a,b) => b.avgRating - a.avgRating);
            const watched = [...stats].sort((a,b) => b.watchCount - a.watchCount);

            document.getElementById('highestRated').innerText = rated[0]?.title || "N/A";
            document.getElementById('topMovie').innerText = watched[0]?.title || "N/A";

            // Render Lists
            renderRanking('top5Rated', rated.slice(0, 5), 'avgRating', '★');
            renderRanking('bottom5Rated', [...rated].reverse().slice(0, 5), 'avgRating', '★');
            
            // Render Tallies
            renderTally('topDirectors', tallies.directors);
            renderTally('topGenres', tallies.genres);
            renderTally('topActors', tallies.actors);
        }

        function renderRanking(id, data, key, unit) {
            const el = document.getElementById(id);
            el.innerHTML = data.map((item, i) => `
                <div class="flex justify-between items-center bg-gray-900/50 p-2 rounded-lg">
                    <span class="text-xs font-bold truncate pr-4">${i+1}. ${item.title}</span>
                    <span class="text-[10px] font-black text-green-400">${key === 'avgRating' ? item[key].toFixed(1) : item[key]}${unit}</span>
                </div>
            `).join('') || '<p class="text-gray-600 text-[10px]">No data</p>';
        }

        function renderTally(id, dataMap) {
            const el = document.getElementById(id);
            const sorted = Object.entries(dataMap)
                .filter(([name]) => name !== "Unknown")
                .sort((a,b) => b[1] - a[1])
                .slice(0, 5);

            el.innerHTML = sorted.map(([name, count]) => `
                <div class="flex justify-between items-center bg-gray-900/30 p-2 rounded-lg">
                    <span class="text-[10px] font-medium truncate pr-2">${name}</span>
                    <span class="text-[10px] font-black text-gray-500">${count}x</span>
                </div>
            `).join('') || '<p class="text-gray-600 text-[10px]">No data</p>';
        }
    </script>
</body>
</html>