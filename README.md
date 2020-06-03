# lol_15ff

##Features
- check match histories and ranks of teammates during champion select
- check match histories and ranks of enemy team in loading screen
- auto accept matches
- predict which team will win using machine learning [(model)](https://github.com/pralphv/lol_15ff_model/)
<img src="/assets/screenshot.png" width="290" height="410"/>

## Instructions
1. Download this [file](/assets/dist.7z)
2. Run dashboard.exe (must be ran in the same directory as static and template)
3. A page will be loaded in your default browser
4. Predictions will be made at 15:00 and 20:00

## Tips
- The model is ~68% accurate when the game is close (kills + assists <= 10) but 90% accurate when kills + assists >= 10
- Be decisive when you are deciding to dodge. You don't have much time before the game starts.
