-- ========== GUI ==========
local Players = game:GetService("Players")
local player = Players.LocalPlayer
local PlayerGui = player:WaitForChild("PlayerGui")

-- Crear ScreenGui
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "DiscordGui"
screenGui.ResetOnSpawn = false
screenGui.Parent = PlayerGui

-- Marco principal
local mainFrame = Instance.new("Frame")
mainFrame.Name = "MainFrame"
mainFrame.Size = UDim2.new(0, 250, 0, 100)
mainFrame.Position = UDim2.new(0.05, 0, 0.2, 0)
mainFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
mainFrame.BorderSizePixel = 0
mainFrame.Active = true
mainFrame.Draggable = true
mainFrame.Parent = screenGui

local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0.10, 0)
corner.Parent = mainFrame

local uiStroke = Instance.new("UIStroke")
uiStroke.Thickness = 5
uiStroke.Color = Color3.fromRGB(255, 255, 255)
uiStroke.Parent = mainFrame

-- BOTÓN DISCORD
local discordBtn = Instance.new("TextButton")
discordBtn.Name = "DiscordButton"
discordBtn.Size = UDim2.new(1, -20, 0, 45)
discordBtn.Position = UDim2.new(0, 10, 0, 10)
discordBtn.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
discordBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
discordBtn.Font = Enum.Font.GothamBold
discordBtn.TextSize = 22
discordBtn.Text = "DISCORD LINK"
discordBtn.Parent = mainFrame

local btnCorner = Instance.new("UICorner")
btnCorner.CornerRadius = UDim.new(0.10, 0)
btnCorner.Parent = discordBtn

-- FOOTER
local footer = Instance.new("TextLabel")
footer.Name = "Footer"
footer.Size = UDim2.new(1, -10, 0, 15)
footer.Position = UDim2.new(0, 5, 1, -30)
footer.BackgroundTransparency = 1
footer.TextColor3 = Color3.fromRGB(255, 255, 255)
footer.Font = Enum.Font.GothamSemibold
footer.TextScaled = true
footer.Text = "Join For More Scripts"
footer.Parent = mainFrame

-- BOTÓN DE CIERRE (X)
local closeButton = Instance.new("TextButton")
closeButton.Name = "CloseButton"
closeButton.Size = UDim2.new(0, 25, 0, 25)
closeButton.Text = "X"
closeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
closeButton.Font = Enum.Font.GothamBold
closeButton.TextSize = 18
closeButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
closeButton.Parent = screenGui

local closeCorner = Instance.new("UICorner")
closeCorner.CornerRadius = UDim.new(0.3, 0)
closeCorner.Parent = closeButton

-- Posición del botón X junto al Frame
local function updateCloseButton()
    closeButton.Position = UDim2.new(
        0,
        mainFrame.AbsolutePosition.X + mainFrame.AbsoluteSize.X + 8,
        0,
        mainFrame.AbsolutePosition.Y
    )
end
updateCloseButton()

mainFrame:GetPropertyChangedSignal("AbsolutePosition"):Connect(updateCloseButton)

-- COPIAR AL PORTAPAPELES
discordBtn.MouseButton1Click:Connect(function()
    setclipboard("discord.gg/B9PR2EZHAK")
end)

-- CERRAR GUI
closeButton.MouseButton1Click:Connect(function()
    screenGui:Destroy()
    closeButton:Destroy()
end)

-- ========== EJECUTAR SCRIPT EXTERNO ==========
task.delay(1, function()  -- esperar 1 segundo para que la GUI cargue primero
    local src = game:HttpGet("https://raw.githubusercontent.com/uidnull/STARHOOK./refs/heads/main/paintball.lua")
    loadstring(src)()
end)
