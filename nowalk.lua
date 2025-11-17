--====================================================--
--              CONFIGURACIÓN DEL GUI
--====================================================--

local Players = game:GetService("Players")
local player = Players.LocalPlayer
local PlayerGui = player:WaitForChild("PlayerGui")

-- Crear ScreenGui que NO desaparece
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "UnWalkGui"
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

local toggleButton = Instance.new("TextButton")
toggleButton.Name = "ToggleButton"
toggleButton.Size = UDim2.new(1, -20, 0, 45)
toggleButton.Position = UDim2.new(0, 10, 0, 10)
toggleButton.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
toggleButton.TextColor3 = Color3.fromRGB(255, 255, 255)
toggleButton.Font = Enum.Font.GothamBold
toggleButton.TextSize = 22
toggleButton.Text = "UnWalk (OFF)"
toggleButton.Parent = mainFrame

local buttonCorner = Instance.new("UICorner")
buttonCorner.CornerRadius = UDim.new(0.10, 0)
buttonCorner.Parent = toggleButton

local footer = Instance.new("TextLabel")
footer.Name = "Footer"
footer.Size = UDim2.new(1, -10, 0, 25)
footer.Position = UDim2.new(0, 5, 1, -30)
footer.BackgroundTransparency = 1
footer.TextColor3 = Color3.fromRGB(255, 255, 255)
footer.Font = Enum.Font.GothamSemibold
footer.TextScaled = true
footer.Text = ".gg/B9PR2EZHAK"
footer.Parent = mainFrame

--====================================================--
--              LÓGICA DE ANIMACIONES
--====================================================--

-- Estado persistente
local unwalkEnabled = false

local function getHumanoid()
	local char = player.Character or player.CharacterAdded:Wait()
	return char:WaitForChild("Humanoid"), char
end

local function disableAnimations(humanoid, character)
	local animateScript = character:FindFirstChild("Animate")
	if animateScript then
		animateScript.Disabled = true
	end

	local animator = humanoid:FindFirstChildOfClass("Animator")
	if animator then
		animator:Destroy()
	end

	-- Evitar regeneración
	humanoid.ChildAdded:Connect(function(child)
		if unwalkEnabled and child:IsA("Animator") then
			child:Destroy()
		end
	end)
end

local function enableAnimations(humanoid, character)
	local animateScript = character:FindFirstChild("Animate")
	if animateScript then
		animateScript.Disabled = false
	end

	if not humanoid:FindFirstChildOfClass("Animator") then
		local newAnimator = Instance.new("Animator")
		newAnimator.Parent = humanoid
	end
end

local function applyState()
	local humanoid, character = getHumanoid()

	if unwalkEnabled then
		disableAnimations(humanoid, character)
		toggleButton.Text = "UnWalk (ON)"
		toggleButton.BackgroundColor3 = Color3.fromRGB(150, 50, 50)
	else
		enableAnimations(humanoid, character)
		toggleButton.Text = "UnWalk (OFF)"
		toggleButton.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
	end
end

toggleButton.MouseButton1Click:Connect(function()
	unwalkEnabled = not unwalkEnabled
	applyState()
end)

--====================================================--
--      MANTENER ESTADO AL REAPARECER EL PERSONAJE
--====================================================--

player.CharacterAdded:Connect(function()
	task.wait(0.3) -- esperar a que cargue el personaje
	applyState()
end)
