#!/usr/bin/env python
__author__ = "Arana Fireheart"

from os import environ
from os.path import join
import re
import pytest

try:
    studentFilesLocation = environ["STUDENT"]
except KeyError:
    studentFilesLocation = ''

try:
    gradingFilesLocation = environ["FIXTURES"]
except KeyError:
    gradingFilesLocation = ''

# noinspection SpellCheckingInspection
ASSIGNMENTFILENAME = "regexpatterns.txt"
# noinspection SpellCheckingInspection
ASSIGNEDNUMBEROFPATTERNS = 7
# noinspection SpellCheckingInspection
TESTSTRINGSFILENAME = "testStrings.txt"


class RegexSolutionsProvided(object):
    def __init__(self, patternFilename):
        self.nonZeroLengthPatternCount = 0
        self.patternDictionary = {}
        self.getStudentSolutionPatterns(patternFilename)

    def getStudentSolutionPatterns(self, patternFile):
        try:
            with open(patternFile, 'r') as inputPatternFile:
                for count, pattern in enumerate(inputPatternFile.readlines()):
                    self.patternDictionary[count + 1] = pattern.strip()
                    if len(pattern.strip()) > 0:
                        self.incrementPatternCount()
        except FileNotFoundError:
            assert False, f"Pattern file {patternFile} not found or not named properly."
        if len(self.patternDictionary) != ASSIGNEDNUMBEROFPATTERNS:
            for count in range(len(self.patternDictionary), ASSIGNEDNUMBEROFPATTERNS + 1):
                self.patternDictionary[count] = ""
        return self.nonZeroLengthPatternCount, self.patternDictionary

    def getPatternCount(self):
        return self.nonZeroLengthPatternCount

    def getPattern(self, patternNumber):
        return self.patternDictionary[patternNumber]

    def incrementPatternCount(self):
        self.nonZeroLengthPatternCount += 1


class TestStrings(object):
    def __init__(self, stringsFilename):
        self.testStrings = {}
        self.getTestStrings(stringsFilename)

    def getTestStrings(self, fileName):
            currentAssignment = -1
            testsList = []
            with open(fileName, 'r') as testInput:
                for string in testInput.readlines():
                    testString = string.strip().split('\t')
                    if int(testString[0]) + 1 != currentAssignment:  # Found beginning of new assignment.
                        if currentAssignment >= 0:
                            self.testStrings[currentAssignment] = testsList  # Stash the last list
                        currentAssignment = int(testString[0]) + 1
                        testsList = [testString[1:]]
                    else:
                        if len(testsList) != 0:  # Not the first entry in list
                            testsList.append(testString[1:])
                self.testStrings[currentAssignment] = testsList  # Stash the last one before leaving

    def getStrings(self, testNumber):
        return self.testStrings[testNumber]


def regexPatternTest(patternNumber, pattern, excerciseTestStrings):
    studentGrades = []
    resultsExpectedForGrades = []
    resultsGeneratedForGrades = []
    for testString in excerciseTestStrings:
        if len(testString) == 2:
            mode, testString = testString
            if mode == "Match":
                resultsExpectedForGrades.append(str(testString))
            else:
                resultsExpectedForGrades.append(None)
        elif len(testString) == 3:
            mode, testString, capturedData = testString
            resultsExpectedForGrades.append(str(capturedData))
        else:
            resultsExpectedForGrades.append(None)
            raise ValueError
        if len(pattern) > 0:
            try:
                if mode == "Match":
                    matchObj = re.match(pattern, testString)
                    if matchObj is not None:
                        resultsGeneratedForGrades.append(matchObj.string)
                    else:
                        resultsGeneratedForGrades.append("None")
                    if matchObj:
                        if matchObj.string == testString:
                            studentGrades.append(10)
                    else:
                        studentGrades.append(0)
                elif mode == "Capture":
                    matchObj = re.findall(pattern, testString)
                    if matchObj is not None:
                        if isinstance(matchObj, list):
                            if len(matchObj) == 0:
                                resultsGeneratedForGrades.append("None")
                            elif len(matchObj) == 1:
                                if isinstance(matchObj[0], str):
                                    resultsGeneratedForGrades.append(matchObj[0])
                                elif isinstance(matchObj[0], tuple):
                                    combinedString = ""
                                    for item in matchObj[0]:
                                        if item != "":
                                            combinedString += item + ' '
                                    resultsGeneratedForGrades.append(combinedString.strip())
                                else:
                                    resultsGeneratedForGrades.append("splat")
                            elif len(matchObj) > 1:
                                if isinstance(matchObj, list):
                                    combinedString = ""
                                    for entry in matchObj:
                                        if isinstance(entry, str):
                                            combinedString += entry + ' '
                                        elif isinstance(entry, tuple):
                                            combinedString += entry[0] + ' '
                                    resultsGeneratedForGrades.append(combinedString.strip())
                    else:
                        resultsGeneratedForGrades.append("None")
                    if matchObj:
                        if type(matchObj) is list:
                            foundData = []
                            if type(matchObj[0]) is tuple:
                                [foundData.append(result) for stringList in matchObj for result in
                                 stringList]
                            else:
                                foundData.extend(matchObj)
                            if '' in foundData:
                                del foundData[foundData.index('')]
                            answers = capturedData.split()
                            if len(answers) == len(foundData):
                                for answer in answers:
                                    if answer not in foundData:
                                        studentGrades.append(0)
                                        break
                                studentGrades.append(10)
                            else:
                                studentGrades.append(0)
                        elif capturedData in foundData:
                            studentGrades.append(10)
                        else:
                            studentGrades.append(0)
                    else:
                        studentGrades.append(0)
                elif mode == "CaptureSp":
                    matchObj = re.findall(pattern, testString)
                    if matchObj is not None and len(matchObj) > 0:
                        resultsGeneratedForGrades.append(matchObj[0])
                    else:
                        resultsGeneratedForGrades.append("None")
                    if matchObj:
                        if type(capturedData) is str:
                            if capturedData == matchObj[0]:
                                studentGrades.append(10)
                        else:
                            studentGrades.append(0)
                    else:
                        studentGrades.append(0)
                elif mode == "Skip":
                    matchObj = re.match(pattern, testString)
                    if matchObj is None:
                        resultsGeneratedForGrades.append("None")
                        studentGrades.append(10)
                    else:
                        resultsGeneratedForGrades.append(matchObj.string)
                        studentGrades.append(0)
                else:
                    print(f"Error unknown mode: {mode}")
            except re.error:
                resultsGeneratedForGrades.append("re.error")
                studentGrades.append(0)
    for position, expectedResult in enumerate(resultsExpectedForGrades):
        if expectedResult is not None:
            if expectedResult != resultsGeneratedForGrades[position]:
                return False, resultsExpectedForGrades, resultsGeneratedForGrades
        elif expectedResult is resultsGeneratedForGrades[position]:
            return False, resultsExpectedForGrades, resultsGeneratedForGrades
    return True, resultsExpectedForGrades, resultsGeneratedForGrades


def test_ProvidedAllSolutions():
    patternFile = join(studentFilesLocation, ASSIGNMENTFILENAME)
    studentSolutions = RegexSolutionsProvided(patternFile)

    if studentSolutions.getPatternCount() == ASSIGNEDNUMBEROFPATTERNS:
        assert True
    else:
        assert False, f"Only found {studentSolutions.getPatternCount()} patterns in {patternFile} file."


@pytest.fixture(scope="module")
def test_getPatternToTest():
    patternFile = join(studentFilesLocation, ASSIGNMENTFILENAME)
    studentSolutions = RegexSolutionsProvided(patternFile)
    return studentSolutions


@pytest.fixture(scope="module")
def test_getTestStringForTest():
    assignmentTestStrings = TestStrings(TESTSTRINGSFILENAME)
    return assignmentTestStrings


@pytest.mark.parametrize(
    "exerciseNumber, regexPattern, testStrings",
    [
        (1, "test_getPatternToTest", "test_getTestStringForTest"),
        (2, "test_getPatternToTest", "test_getTestStringForTest"),
        (3, "test_getPatternToTest", "test_getTestStringForTest"),
        (4, "test_getPatternToTest", "test_getTestStringForTest"),
        (5, "test_getPatternToTest", "test_getTestStringForTest"),
        (6, "test_getPatternToTest", "test_getTestStringForTest"),
        (7, "test_getPatternToTest", "test_getTestStringForTest"),
    ],
    ids=[
        "exercise1",
        "exercise2",
        "exercise3",
        "exercise4",
        "exercise5",
        "exercise6",
        "exercise7",
        ],
)
def test_PatternWorks(exerciseNumber, regexPattern, testStrings, request):
    studentPatterns = request.getfixturevalue(regexPattern)
    patternToTest = studentPatterns.getPattern(exerciseNumber)
    testStringsObject = request.getfixturevalue(testStrings)
    excerciseTestStrings = testStringsObject.getStrings(exerciseNumber)
    testResults, expectedResults, generatedResults = regexPatternTest(exerciseNumber, patternToTest, excerciseTestStrings)

    if testResults:
        assert True
    else:
        assert False, f"Pattern didn't work.\n Expected: {expectedResults} Actual: {generatedResults}"
